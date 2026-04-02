import { AUTH_STORAGE_KEYS, getAuthStorageValue } from '@/platform/auth-storage'

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
