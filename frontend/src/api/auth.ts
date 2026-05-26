import apiClient from './index'

export function login(username: string, password: string) {
  return apiClient.post('/auth/login', { username, password })
}

export function refresh(refreshToken: string) {
  return apiClient.post('/auth/refresh', { refresh_token: refreshToken })
}

export function logout(refreshToken: string) {
  return apiClient.post('/auth/logout', { refresh_token: refreshToken })
}
