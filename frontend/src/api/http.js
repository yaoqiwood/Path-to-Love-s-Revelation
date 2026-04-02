import axios from 'axios'
import { shouldUseMock, withMockFallback } from './mockService'
import {
  getAuthStorageValue,
  removeAuthStorageValue,
  AUTH_STORAGE_KEYS
} from '@/platform/auth-storage'

function normalizeBaseUrl(value) {
  const normalizedValue = String(value || '').trim()
  if (!normalizedValue || normalizedValue === '/') {
    return ''
  }

  return normalizedValue.endsWith('/') ? normalizedValue.slice(0, -1) : normalizedValue
}

function normalizeRequestUrl(url = '') {
  const normalizedUrl = String(url || '').trim()
  return normalizedUrl.replace(/^\/api\/api(\/|$)/, '/api$1')
}

const apiBaseUrl = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL)
const USER_LOGIN_PATH = '/pages/index/login-home'
const ADMIN_LOGIN_PATH = '/pages/index/admin-login-home'
const API_TESTER_PATH = '/api_tester'
const API_TESTER_ALIAS_PATH = '/api-tester'

export { shouldUseMock } from './mockService'

export const http = axios.create({
  baseURL: apiBaseUrl,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

function buildRequestId() {
  return `req-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

function resolveLoginPath() {
  if (typeof window === 'undefined') {
    return USER_LOGIN_PATH
  }

  return window.location.pathname.startsWith('/pkg/guide/') ? ADMIN_LOGIN_PATH : USER_LOGIN_PATH
}

http.interceptors.request.use((config) => {
  config.headers = config.headers || {}
  config.headers.Accept = 'application/json'
  config.headers['X-Requested-With'] = 'XMLHttpRequest'
  config.headers['X-Request-Id'] = buildRequestId()
  config.url = normalizeRequestUrl(config.url)

  const hasAuthorizationHeader = !!(config.headers.Authorization || config.headers.authorization)
  const session = getAuthStorageValue(AUTH_STORAGE_KEYS.session)
  if (session?.token && !config.skipUserSessionAuth && !hasAuthorizationHeader) {
    config.headers.Authorization = `Bearer ${session.token}`
  }

  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = Number(error?.response?.status || 0)
    const skipAuthRedirect = error?.config?.skipAuthRedirect === true

    if (error?.response?.data) {
      const message =
        error.response.data.message ||
        error.response.data.errMsg ||
        error.response.data.error ||
        error.message
      error.message = message
    } else if (error?.code === 'ECONNABORTED') {
      error.message = '请求超时，请稍后重试。'
    } else if (!error?.response) {
      error.message = '网络异常，请检查后端服务或代理配置。'
    }

    if (status === 401 && !skipAuthRedirect) {
      removeAuthStorageValue(AUTH_STORAGE_KEYS.profile)
      removeAuthStorageValue(AUTH_STORAGE_KEYS.session)

      if (typeof window !== 'undefined') {
        const loginPath = resolveLoginPath()
        if (
          window.location.pathname !== USER_LOGIN_PATH &&
          window.location.pathname !== ADMIN_LOGIN_PATH &&
          window.location.pathname !== API_TESTER_PATH &&
          window.location.pathname !== API_TESTER_ALIAS_PATH
        ) {
          window.location.replace(loginPath)
        }
      }
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
