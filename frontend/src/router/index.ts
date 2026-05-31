import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

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

// Navigation guard
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  const isPublic = to.meta.public

  if (!token && !isPublic) {
    next('/login')
    return
  }

  if (token && isPublic) {
    next('/')
    return
  }

  next()
})

export default router
