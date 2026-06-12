import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router'

/** Idle timeout in milliseconds (10 min). */
const IDLE_TIMEOUT_MS = 10 * 60 * 1000

/** User activity events to listen on. */
const _IDLE_EVENTS = ['mousedown', 'keydown', 'touchstart', 'scroll'] as const

interface UserInfo {
  id: number
  username: string
  role: string
}

function _loadUser(): UserInfo | null {
  try {
    const raw = localStorage.getItem('user_info')
    return raw ? (JSON.parse(raw) as UserInfo) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const user = ref<UserInfo | null>(_loadUser())

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const username = computed(() => user.value?.username || '')

  /* ── Idle timeout ── */

  let idleTimer: ReturnType<typeof setTimeout> | null = null
  let idleDetectionStarted = false

  function _resetIdleTimer() {
    if (idleTimer) clearTimeout(idleTimer)
    if (!token.value) return
    idleTimer = setTimeout(() => {
      logout()
      // eslint-disable-next-line no-alert
      alert('长时间未操作，已自动退出登录')
    }, IDLE_TIMEOUT_MS)
  }

  /** Start listening for user activity. Safe to call multiple times. */
  function startIdleDetection() {
    if (idleDetectionStarted) return
    idleDetectionStarted = true
    _IDLE_EVENTS.forEach((event) =>
      window.addEventListener(event, _resetIdleTimer),
    )
    _resetIdleTimer()
  }

  /** Stop idle detection (e.g. on logout). */
  function stopIdleDetection() {
    if (idleTimer) clearTimeout(idleTimer)
    idleTimer = null
    idleDetectionStarted = false
    _IDLE_EVENTS.forEach((event) =>
      window.removeEventListener(event, _resetIdleTimer),
    )
  }

  /* ── Token / user management ── */

  function setTokens(access: string, refresh: string) {
    token.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    startIdleDetection()
  }

  function setUser(userInfo: UserInfo) {
    user.value = userInfo
    localStorage.setItem('user_info', JSON.stringify(userInfo))
    localStorage.setItem('last_username', userInfo.username)
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
    stopIdleDetection()
    router.push('/login')
  }

  return {
    token,
    refreshToken,
    user,
    isLoggedIn,
    isAdmin,
    username,
    setTokens,
    setUser,
    logout,
    startIdleDetection,
    stopIdleDetection,
  }
})
