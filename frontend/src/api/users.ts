import apiClient from './index'

export interface UserCreateData {
  username: string
  password: string
  email?: string
  role?: string
  enabled?: boolean
  note?: string
}

export interface UserUpdateData {
  email?: string
  password?: string
  role?: string
  enabled?: boolean
  note?: string
}

export function getUsers(params: {
  page?: number
  page_size?: number
  search?: string
  enabled?: boolean | null
}) {
  return apiClient.get('/users', { params })
}

export function getUser(id: number) {
  return apiClient.get(`/users/${id}`)
}

export function createUser(data: UserCreateData) {
  return apiClient.post('/users', data)
}

export function updateUser(id: number, data: UserUpdateData) {
  return apiClient.put(`/users/${id}`, data)
}

export function deleteUser(id: number) {
  return apiClient.delete(`/users/${id}`)
}

export function resetPassword(id: number, newPassword: string) {
  return apiClient.put(`/users/${id}/reset-password`, { new_password: newPassword })
}

export function getUserOtpStatus(id: number) {
  return apiClient.get(`/users/${id}/otp-status`)
}

export function adminDisableUserOtp(id: number) {
  return apiClient.delete(`/users/${id}/otp`)
}
