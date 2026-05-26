import apiClient from './index'

export interface NasCreateData {
  shortname: string
  ip_address: string
  secret: string
  nas_type?: string
  description?: string
  enabled?: boolean
}

export interface NasUpdateData {
  shortname?: string
  ip_address?: string
  secret?: string
  nas_type?: string
  description?: string
  enabled?: boolean
}

export function getNasClients(params: { page?: number; page_size?: number }) {
  return apiClient.get('/nas-clients', { params })
}

export function getNasClient(id: number) {
  return apiClient.get(`/nas-clients/${id}`)
}

export function createNasClient(data: NasCreateData) {
  return apiClient.post('/nas-clients', data)
}

export function updateNasClient(id: number, data: NasUpdateData) {
  return apiClient.put(`/nas-clients/${id}`, data)
}

export function deleteNasClient(id: number) {
  return apiClient.delete(`/nas-clients/${id}`)
}

export function generateConfig() {
  return apiClient.get('/nas-clients/generate-config', { responseType: 'text' })
}

export function syncNasConfig() {
  return apiClient.post('/nas-clients/sync')
}
