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

function resolveOptionalString(...values) {
  for (const value of values) {
    const normalizedValue = String(value || '').trim()
    if (normalizedValue) {
      return normalizedValue
    }
  }

  return ''
}

function resolveOptionalNumber(...values) {
  for (const value of values) {
    const normalizedValue = Number(value)
    if (Number.isFinite(normalizedValue)) {
      return normalizedValue
    }
  }

  return null
}

function getStoredValidationSnapshot() {
  const profile = getAuthStorageValue(AUTH_STORAGE_KEYS.profile)
  const session = getAuthStorageValue(AUTH_STORAGE_KEYS.session)

  return {
    user_type: resolveOptionalString(
      profile?.user_type,
      profile?.userType,
      session?.userType,
      session?.user_type,
      session?.userInfo?.user_type,
      session?.userInfo?.userType
    ),
    user_role: resolveOptionalNumber(
      profile?.user_role,
      profile?.userRole,
      session?.userRole,
      session?.user_role,
      session?.userInfo?.user_role,
      session?.userInfo?.userRole
    )
  }
}

function isExplicitInvalidValidationResult(result) {
  const authFlags = [
    result?.valid,
    result?.is_valid,
    result?.isValid,
    result?.authenticated,
    result?.is_authenticated
  ]

  if (authFlags.some((value) => value === false)) {
    return true
  }

  const authStatus = String(result?.status || result?.auth_status || '').trim().toLowerCase()
  return authStatus === 'invalid' || authStatus === 'expired' || authStatus === 'unauthorized'
}

function normalizeValidatedUser(result) {
  if (isExplicitInvalidValidationResult(result)) {
    return null
  }

  const storedSnapshot = getStoredValidationSnapshot()
  const candidates = [
    result,
    result?.data,
    result?.profile,
    result?.user,
    result?.current_user,
    result?.currentUser
  ].filter((item) => item && typeof item === 'object')

  const userType = resolveOptionalString(
    ...candidates.flatMap((item) => [item.user_type, item.userType]),
    storedSnapshot.user_type
  )
  const userRole = resolveOptionalNumber(
    ...candidates.flatMap((item) => [item.user_role, item.userRole]),
    storedSnapshot.user_role
  )

  return {
    user_type: userType,
    user_role: userRole
  }
}

function syncValidatedUser(validatedUser) {
  const userType = resolveOptionalString(validatedUser?.user_type)
  const userRole = resolveOptionalNumber(validatedUser?.user_role)

  const profile = getAuthStorageValue(AUTH_STORAGE_KEYS.profile)
  if (profile && typeof profile === 'object') {
    const nextProfile = {
      ...profile,
      cached_at: Date.now()
    }
    if (userType) {
      nextProfile.user_type = userType
    }
    if (Number.isFinite(userRole)) {
      nextProfile.user_role = userRole
    }
    setAuthStorageValue(AUTH_STORAGE_KEYS.profile, nextProfile)
  }

  const session = getAuthStorageValue(AUTH_STORAGE_KEYS.session)
  if (session && typeof session === 'object') {
    const nextSession = {
      ...session,
      validatedAt: Date.now()
    }
    if (userType) {
      nextSession.userType = userType
    }
    if (Number.isFinite(userRole)) {
      nextSession.userRole = userRole
    }
    setAuthStorageValue(AUTH_STORAGE_KEYS.session, nextSession)
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
