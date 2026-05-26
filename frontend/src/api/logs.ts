import apiClient from './index'

export function getAuthLogs(params: {
  page?: number
  page_size?: number
  username?: string
  start_date?: string
  end_date?: string
  result?: string
}) {
  return apiClient.get('/logs/auth', { params })
}

export function getOnlineUsers(params: { page?: number; page_size?: number }) {
  return apiClient.get('/logs/online', { params })
}

export function getDashboardStats() {
  return apiClient.get('/dashboard/stats')
}
