import axios from 'axios'
import { shouldUseMock, withMockFallback } from './mockService'

const apiBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim()

export { shouldUseMock } from './mockService'

export const http = axios.create({
  baseURL: apiBaseUrl,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

http.interceptors.request.use((config) => {
  const sessionText = localStorage.getItem('app-auth-session')
  if (sessionText) {
    try {
      const session = JSON.parse(sessionText)
      if (session?.token) {
        config.headers.Authorization = `Bearer ${session.token}`
      }
    } catch (error) {
      console.warn('Failed to parse app-auth-session before request.', error)
    }
  }

  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.data) {
      const message =
        error.response.data.message ||
        error.response.data.errMsg ||
        error.response.data.error ||
        error.message
      error.message = message
    }

    return Promise.reject(error)
  }
)

export function unwrapResponse(response) {
  return response?.data ?? response
}

export async function get(url, config = {}, mockHandler) {
  return withMockFallback(
    async () => unwrapResponse(await http.get(url, config)),
    mockHandler,
    {
      method: 'get',
      url,
      config
    }
  )
}

export async function post(url, data = {}, config = {}, mockHandler) {
  return withMockFallback(
    async () => unwrapResponse(await http.post(url, data, config)),
    mockHandler,
    {
      method: 'post',
      url,
      data,
      config
    }
  )
}
