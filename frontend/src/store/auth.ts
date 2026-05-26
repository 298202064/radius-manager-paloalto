import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router'

interface UserInfo {
  id: number
  username: string
  role: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const username = computed(() => user.value?.username || '')

  function setTokens(access: string, refresh: string) {
    token.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function setUser(userInfo: UserInfo) {
    user.value = userInfo
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
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
  }
})
