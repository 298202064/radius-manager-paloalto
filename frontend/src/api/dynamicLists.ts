import apiClient from './index'

export interface DynamicListResponse {
  lines: string[]
  total: number
}

export function getIPList() {
  return apiClient.get<DynamicListResponse>('/dynamic-lists/ip')
}

export function updateIPList(lines: string[]) {
  return apiClient.put<DynamicListResponse>('/dynamic-lists/ip', { lines })
}

export function getURLList() {
  return apiClient.get<DynamicListResponse>('/dynamic-lists/url')
}

export function updateURLList(lines: string[]) {
  return apiClient.put<DynamicListResponse>('/dynamic-lists/url', { lines })
}
