import apiClient from './index'

export interface GatewayCreateData {
  name: string
  host: string
  username: string
  password: string
  description?: string
  enabled?: boolean
}

export interface GatewayUpdateData {
  name?: string
  host?: string
  username?: string
  password?: string
  description?: string
  enabled?: boolean
}

export function getGateways(params: { page?: number; page_size?: number }) {
  return apiClient.get('/gateways', { params })
}

export function getGateway(id: number) {
  return apiClient.get(`/gateways/${id}`)
}

export function createGateway(data: GatewayCreateData) {
  return apiClient.post('/gateways', data)
}

export function updateGateway(id: number, data: GatewayUpdateData) {
  return apiClient.put(`/gateways/${id}`, data)
}

export function deleteGateway(id: number) {
  return apiClient.delete(`/gateways/${id}`)
}

export function testGateway(id: number) {
  return apiClient.post(`/gateways/${id}/test`)
}

export function getGatewayOnlineUsers() {
  return apiClient.get('/gateways/online-users')
}
