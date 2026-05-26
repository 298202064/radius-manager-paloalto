import apiClient from './index'

export interface LDAPConfigCreateData {
  name: string
  host: string
  port?: number
  base_dn: string
  bind_dn: string
  bind_password: string
  use_tls?: boolean
  description?: string
  enabled?: boolean
}

export interface LDAPConfigUpdateData {
  name?: string
  host?: string
  port?: number
  base_dn?: string
  bind_dn?: string
  bind_password?: string
  use_tls?: boolean
  description?: string
  enabled?: boolean
}

export function getLDAPConfigs(params: { page?: number; page_size?: number }) {
  return apiClient.get('/ldap/configs', { params })
}

export function getLDAPConfig(id: number) {
  return apiClient.get(`/ldap/configs/${id}`)
}

export function createLDAPConfig(data: LDAPConfigCreateData) {
  return apiClient.post('/ldap/configs', data)
}

export function updateLDAPConfig(id: number, data: LDAPConfigUpdateData) {
  return apiClient.put(`/ldap/configs/${id}`, data)
}

export function deleteLDAPConfig(id: number) {
  return apiClient.delete(`/ldap/configs/${id}`)
}

export function testLDAPConnection(id: number) {
  return apiClient.post(`/ldap/configs/${id}/test`)
}

export function searchADUsers(id: number, data: { search_filter?: string; search_base?: string }) {
  return apiClient.post(`/ldap/configs/${id}/search`, data)
}

export function importADUsers(id: number, data: { usernames: string[] }) {
  return apiClient.post(`/ldap/configs/${id}/import`, data)
}
