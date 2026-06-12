import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

/**
 * Decode a JWT payload without verifying the signature (frontend-only check).
 * Returns null for any parse failure.
 */
function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    return JSON.parse(atob(parts[1]))
  } catch {
    return null
  }
}

function isTokenExpired(token: string): boolean {
  const payload = decodeJwtPayload(token)
  if (!payload || typeof payload.exp !== 'number') return true
  return payload.exp * 1000 < Date.now()
}

/** Clear both tokens from storage. */
function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/components/AppLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '仪表盘', roles: ['admin'] },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/UserListView.vue'),
        meta: { title: '用户管理', roles: ['admin'] },
      },
      {
        path: 'nas-clients',
        name: 'NasClients',
        component: () => import('@/views/nas/NasListView.vue'),
        meta: { title: 'NAS客户端', roles: ['admin'] },
      },
      {
        path: 'gateways',
        name: 'Gateways',
        component: () => import('@/views/gateways/GatewayListView.vue'),
        meta: { title: '只读网关', roles: ['admin'] },
      },
      {
        path: 'ldap',
        name: 'LDAP',
        component: () => import('@/views/ldap/LDAPListView.vue'),
        meta: { title: '只读LDAP', roles: ['admin'] },
      },
      {
        path: 'dynamic-lists',
        name: 'DynamicLists',
        component: () => import('@/views/dynamicLists/DynamicListsView.vue'),
        meta: { title: '动态列表', roles: ['admin'] },
      },
      {
        path: 'logs/auth',
        name: 'AuthLogs',
        component: () => import('@/views/logs/AuthLogView.vue'),
        meta: { title: '认证日志', roles: ['admin'] },
      },
      {
        path: 'logs/online',
        name: 'OnlineUsers',
        component: () => import('@/views/logs/OnlineUserView.vue'),
        meta: { title: '在线用户', roles: ['admin'] },
      },
      {
        path: 'self/password',
        name: 'ChangePassword',
        component: () => import('@/views/self/ChangePasswordView.vue'),
        meta: { title: '修改密码' },
      },
      {
        path: 'self/otp',
        name: 'OtpManage',
        component: () => import('@/views/self/OtpManageView.vue'),
        meta: { title: 'OTP管理' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard — check token existence AND expiry
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  const isPublic = to.meta.public

  // No token → public pages are OK, everything else redirects
  if (!token) {
    if (isPublic) return next()
    return next('/login')
  }

  // Token exists but expired → clear and redirect to login
  if (isTokenExpired(token)) {
    clearTokens()
    if (isPublic) return next()
    return next('/login')
  }

  // Valid token on a public page (e.g. /login) → redirect to dashboard
  if (isPublic) return next('/')

  next()
})

export default router
