import apiClient from './index'

export function changePassword(currentPassword: string, newPassword: string) {
  return apiClient.put('/self/password', {
    current_password: currentPassword,
    new_password: newPassword,
  })
}

export function getOtpQrcode() {
  return apiClient.get('/self/otp/qrcode')
}

export function bindOtp(token: string) {
  return apiClient.post('/self/otp/bind', { token })
}

export function unbindOtp() {
  return apiClient.delete('/self/otp')
}

export function getOtpStatus() {
  return apiClient.get('/self/otp/status')
}
