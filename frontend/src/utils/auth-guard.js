import { userService } from '@/api/modules/user'
import {
  AUTH_STORAGE_KEYS,
  getAuthStorageValue,
  removeAuthStorageValue,
  setAuthStorageValue
} from '@/platform/auth-storage'

export const USER_LOGIN_PATH = '/pages/index/login-home'
export const ADMIN_LOGIN_PATH = '/pages/index/admin-login-home'
export const API_TESTER_PATH = '/api_tester'
export const API_TESTER_ALIAS_PATH = '/api-tester'
const POST_LOGIN_HANDOFF_STORAGE_KEY = 'post-login-auth-handoff'

let pendingTokenValidation = null

function normalizeValidatedUser(result) {
  const userType = String(result?.user_type || '').trim()
  const userRole = Number(result?.user_role)

  if (!userType || !Number.isFinite(userRole)) {
    return null
  }

  return {
    user_type: userType,
    user_role: userRole
  }
}

function syncValidatedUser(validatedUser) {
  const profile = getAuthStorageValue(AUTH_STORAGE_KEYS.profile)
  if (profile && typeof profile === 'object') {
    setAuthStorageValue(AUTH_STORAGE_KEYS.profile, {
      ...profile,
      user_type: validatedUser.user_type,
      user_role: validatedUser.user_role,
      cached_at: Date.now()
    })
  }

  const session = getAuthStorageValue(AUTH_STORAGE_KEYS.session)
  if (session && typeof session === 'object') {
    setAuthStorageValue(AUTH_STORAGE_KEYS.session, {
      ...session,
      userType: validatedUser.user_type,
      userRole: validatedUser.user_role,
      validatedAt: Date.now()
    })
  }
}

export function clearAuthSession() {
  removeAuthStorageValue(AUTH_STORAGE_KEYS.profile)
  removeAuthStorageValue(AUTH_STORAGE_KEYS.session)
}

export function getStoredAccessToken() {
  const session = getAuthStorageValue(AUTH_STORAGE_KEYS.session)
  return String(session?.token || session?.accessToken || '').trim()
}

export function resolveLoginPathByRoutePath(path = '') {
  return String(path || '').startsWith('/pkg/guide/') ? ADMIN_LOGIN_PATH : USER_LOGIN_PATH
}

export function markPostLoginHandoff(path = '') {
  if (typeof window === 'undefined') {
    return
  }

  try {
    window.sessionStorage.setItem(
      POST_LOGIN_HANDOFF_STORAGE_KEY,
      JSON.stringify({
        path: String(path || '').trim(),
        createdAt: Date.now()
      })
    )
  } catch (error) {
    // Ignore sessionStorage failures and fall back to normal guard behavior.
  }
}

export function consumePostLoginHandoff(path = '') {
  if (typeof window === 'undefined') {
    return false
  }

  try {
    const rawValue = window.sessionStorage.getItem(POST_LOGIN_HANDOFF_STORAGE_KEY)
    window.sessionStorage.removeItem(POST_LOGIN_HANDOFF_STORAGE_KEY)

    if (!rawValue) {
      return false
    }

    const payload = JSON.parse(rawValue)
    const targetPath = String(path || '').trim()
    const markedPath = String(payload?.path || '').trim()
    const createdAt = Number(payload?.createdAt || 0)
    const isFresh = Number.isFinite(createdAt) && createdAt > 0 && Date.now() - createdAt < 10000

    return !!markedPath && markedPath === targetPath && isFresh
  } catch (error) {
    return false
  }
}

async function requestTokenValidation() {
  const accessToken = getStoredAccessToken()
  if (!accessToken) {
    clearAuthSession()
    return null
  }

  try {
    const result = await userService.validateToken({
      skipAuthRedirect: true
    })
    const validatedUser = normalizeValidatedUser(result)

    if (!validatedUser) {
      clearAuthSession()
      return null
    }

    syncValidatedUser(validatedUser)
    return validatedUser
  } catch (error) {
    if (Number(error?.response?.status || 0) === 401) {
      clearAuthSession()
      return null
    }

    throw error
  }
}

export async function validateStoredToken({ force = false } = {}) {
  if (!force && pendingTokenValidation) {
    return pendingTokenValidation
  }

  const validationPromise = requestTokenValidation().finally(() => {
    if (pendingTokenValidation === validationPromise) {
      pendingTokenValidation = null
    }
  })

  pendingTokenValidation = validationPromise
  return validationPromise
}
