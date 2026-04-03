function getLocalStorageBackend() {
  if (typeof window === 'undefined' || !window.localStorage) {
    return null
  }

  return window.localStorage
}

function cloneValue(value) {
  if (value == null || typeof value !== 'object') {
    return value
  }

  try {
    return JSON.parse(JSON.stringify(value))
  } catch (error) {
    return value
  }
}

export function normalizeStorageKey(key) {
  return String(key)
}

export function parseLocalStorageValue(
  rawValue,
  { fallback = '', preserveRaw = true, treatEmptyAsMissing = false, onError } = {}
) {
  if (rawValue == null || (treatEmptyAsMissing && rawValue === '')) {
    return cloneValue(fallback)
  }

  try {
    return JSON.parse(rawValue)
  } catch (error) {
    onError?.(error)
    return preserveRaw ? rawValue : cloneValue(fallback)
  }
}

export function isLocalStorageAvailable() {
  return Boolean(getLocalStorageBackend())
}

export function hasLocalStorageKey(key) {
  const backend = getLocalStorageBackend()
  if (!backend) {
    return false
  }

  try {
    return backend.getItem(normalizeStorageKey(key)) != null
  } catch (error) {
    return false
  }
}

export function readLocalStorage(
  key,
  { fallback = '', preserveRaw = true, treatEmptyAsMissing = false, onError } = {}
) {
  const backend = getLocalStorageBackend()
  if (!backend) {
    return cloneValue(fallback)
  }

  try {
    const rawValue = backend.getItem(normalizeStorageKey(key))
    return parseLocalStorageValue(rawValue, {
      fallback,
      preserveRaw,
      treatEmptyAsMissing,
      onError
    })
  } catch (error) {
    onError?.(error)
    return cloneValue(fallback)
  }
}

export function writeLocalStorage(key, value, { serialize = true, onError } = {}) {
  const backend = getLocalStorageBackend()
  if (!backend) {
    return false
  }

  try {
    const rawValue = serialize ? JSON.stringify(value) : String(value ?? '')
    backend.setItem(normalizeStorageKey(key), rawValue)
    return true
  } catch (error) {
    onError?.(error)
    return false
  }
}

export function removeLocalStorage(key, { onError } = {}) {
  const backend = getLocalStorageBackend()
  if (!backend) {
    return false
  }

  try {
    backend.removeItem(normalizeStorageKey(key))
    return true
  } catch (error) {
    onError?.(error)
    return false
  }
}

export function removeLocalStorageItems(keys = [], options) {
  return keys.every((key) => removeLocalStorage(key, options))
}

export function createLocalStorageManager({ prefix = '' } = {}) {
  const formatKey = (key) => `${prefix}${normalizeStorageKey(key)}`

  return {
    key: formatKey,
    has(key) {
      return hasLocalStorageKey(formatKey(key))
    },
    get(key, options) {
      return readLocalStorage(formatKey(key), options)
    },
    set(key, value, options) {
      return writeLocalStorage(formatKey(key), value, options)
    },
    remove(key, options) {
      return removeLocalStorage(formatKey(key), options)
    },
    removeMany(keys, options) {
      return removeLocalStorageItems(keys.map((key) => formatKey(key)), options)
    }
  }
}

export const localStorageManager = createLocalStorageManager()
