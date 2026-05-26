import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: inject JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const res = await axios.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken,
          })
          const { access_token, refresh_token } = res.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          router.push('/login')
          ElMessage.error('登录已过期，请重新登录')
        }
      } else {
        router.push('/login')
      }
    }

    // Handle error messages
    const msg = error.response?.data?.detail || error.message
    if (error.response?.status !== 401) {
      ElMessage.error(msg)
    }

    return Promise.reject(error)
  }
)

export default apiClient
