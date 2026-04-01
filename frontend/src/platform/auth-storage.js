export const AUTH_STORAGE_KEYS = {
  profile: 'mbtiPersonnelProfile',
  session: 'app-auth-session'
}

const COOKIE_MAX_AGE_SECONDS = 7 * 24 * 60 * 60

function safeParse(rawValue) {
  if (rawValue == null || rawValue === '') {
    return ''
  }

  try {
    return JSON.parse(rawValue)
  } catch (error) {
    return rawValue
  }
}

function safeStringify(value) {
  try {
    return JSON.stringify(value)
  } catch (error) {
    return '""'
  }
}

function readCookieRaw(name) {
  if (typeof document === 'undefined') {
    return null
  }

  const prefix = `${encodeURIComponent(String(name))}=`
  const segments = String(document.cookie || '').split(';')
  for (let index = 0; index < segments.length; index += 1) {
    const item = segments[index].trim()
    if (item.startsWith(prefix)) {
      return decodeURIComponent(item.slice(prefix.length))
    }
  }

  return null
}

function writeCookieRaw(name, rawValue) {
  if (typeof document === 'undefined') {
    return
  }

  document.cookie =
    `${encodeURIComponent(String(name))}=${encodeURIComponent(String(rawValue))}; ` +
    `Path=/; Max-Age=${COOKIE_MAX_AGE_SECONDS}; SameSite=Lax`
}

function removeCookie(name) {
  if (typeof document === 'undefined') {
    return
  }

  document.cookie = `${encodeURIComponent(String(name))}=; Path=/; Max-Age=0; SameSite=Lax`
}

export function isAuthStorageKey(key) {
  const normalizedKey = String(key)
  return normalizedKey === AUTH_STORAGE_KEYS.profile || normalizedKey === AUTH_STORAGE_KEYS.session
}

export function setAuthStorageValue(key, value) {
  if (!isAuthStorageKey(key)) {
    return false
  }

  const normalizedKey = String(key)
  writeCookieRaw(normalizedKey, safeStringify(value))

  try {
    localStorage.removeItem(normalizedKey)
  } catch (error) {
    // Keep silent to avoid blocking login flow when storage is unavailable.
  }

  return true
}

export function getAuthStorageValue(key) {
  if (!isAuthStorageKey(key)) {
    return null
  }

  const normalizedKey = String(key)
  const cookieValue = readCookieRaw(normalizedKey)
  if (cookieValue != null) {
    return safeParse(cookieValue)
  }

  try {
    return safeParse(localStorage.getItem(normalizedKey))
  } catch (error) {
    return ''
  }
}

export function removeAuthStorageValue(key) {
  if (!isAuthStorageKey(key)) {
    return false
  }

  const normalizedKey = String(key)
  removeCookie(normalizedKey)

  try {
    localStorage.removeItem(normalizedKey)
  } catch (error) {
    // Ignore localStorage removal failures.
  }

  return true
}
