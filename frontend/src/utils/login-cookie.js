import {
  AUTH_STORAGE_KEYS,
  getAuthStorageValue,
  setAuthStorageValue
} from '@/platform/auth-storage'

export const LOGIN_PROFILE_COOKIE_NAME = AUTH_STORAGE_KEYS.profile

export const LOGIN_PROFILE_HOME_PATHS = {
  admin: '/pkg/guide/hub',
  user: '/pages/index/home',
  login: '/pages/index/login-home',
  adminLogin: '/pages/index/admin-login-home'
}

export function getLoginProfileFromCookie() {
  const profile = getAuthStorageValue(LOGIN_PROFILE_COOKIE_NAME)
  return profile && typeof profile === 'object' ? profile : null
}

function decodeJwtPayload(token) {
  const normalizedToken = String(token || '').trim()
  if (!normalizedToken) {
    return null
  }

  const segments = normalizedToken.split('.')
  if (segments.length < 2) {
    return null
  }

  try {
    const base64 = segments[1].replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, '=')
    return JSON.parse(atob(padded))
  } catch (error) {
    return null
  }
}

function resolveTokenExpiredAt(token) {
  const payload = decodeJwtPayload(token)
  const exp = Number(payload && payload.exp)
  return Number.isFinite(exp) && exp > 0 ? exp * 1000 : Date.now() + 7 * 24 * 60 * 60 * 1000
}

function buildStoredProfile(profile = {}) {
  return {
    ...profile,
    id: profile._id || profile.id || '',
    personnel_id: profile._id || profile.personnel_id || profile.id || '',
    person_id: Number(profile.person_id) || 0,
    user_role: Number(profile.user_role) || 0,
    cached_at: Date.now()
  }
}

function buildStoredSession({ profile = {}, accessToken = '', tokenType = 'bearer' } = {}) {
  const avatar = profile.personal_photo || ''
  const uid = profile.user_id || profile._id || profile.id || ''

  return {
    uid,
    token: accessToken,
    tokenType,
    tokenExpired: resolveTokenExpiredAt(accessToken),
    userInfo: {
      _id: uid,
      nickname: profile.nickname || profile.name || '',
      avatar,
      avatar_file: avatar
    }
  }
}

export function applyPersonnelLoginSession({
  profile = {},
  accessToken = '',
  tokenType = 'bearer'
} = {}) {
  const storedProfile = buildStoredProfile(profile)
  const storedSession = buildStoredSession({
    profile: storedProfile,
    accessToken,
    tokenType
  })

  setAuthStorageValue(AUTH_STORAGE_KEYS.profile, storedProfile)
  setAuthStorageValue(AUTH_STORAGE_KEYS.session, storedSession)

  return {
    profile: storedProfile,
    session: storedSession
  }
}

export function hasLoginProfileCookie(profile) {
  return !!(
    profile &&
    typeof profile === 'object' &&
    ('user_role' in profile ||
      'userRole' in profile ||
      profile._id ||
      profile.id ||
      profile.personnel_id)
  )
}

export function isAdminUserRole(roleValue) {
  const role = Number(roleValue)
  return role === 1 || role === 2 || role === 3
}

export function getLoginProfileUserRole(profile) {
  if (!profile || typeof profile !== 'object') {
    return null
  }

  if ('user_role' in profile) {
    return Number(profile.user_role) || 0
  }

  if ('userRole' in profile) {
    return Number(profile.userRole) || 0
  }

  return null
}

export function resolveHomePathByLoginProfile(
  profile,
  { fallbackPath = LOGIN_PROFILE_HOME_PATHS.login } = {}
) {
  if (!hasLoginProfileCookie(profile)) {
    return fallbackPath
  }

  const userRole = getLoginProfileUserRole(profile)
  if (userRole == null) {
    return fallbackPath
  }

  return isAdminUserRole(userRole)
    ? LOGIN_PROFILE_HOME_PATHS.admin
    : LOGIN_PROFILE_HOME_PATHS.user
}
