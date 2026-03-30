const explicitMockValue = String(import.meta.env.VITE_USE_MOCK || '')
  .trim()
  .toLowerCase()
const apiBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim()

export const shouldUseMock =
  explicitMockValue === 'true' ||
  explicitMockValue === '1' ||
  explicitMockValue === 'yes' ||
  !apiBaseUrl

function hasMockHandler(mockHandler) {
  return typeof mockHandler !== 'undefined'
}

export async function resolveMock(mockHandler, context = {}) {
  if (typeof mockHandler === 'function') {
    return mockHandler(context)
  }

  return mockHandler
}

export async function withMockFallback(requestFactory, mockHandler, context = {}) {
  if (typeof requestFactory !== 'function') {
    throw new TypeError('requestFactory must be a function')
  }

  if (!hasMockHandler(mockHandler)) {
    return requestFactory(context)
  }

  if (shouldUseMock) {
    return resolveMock(mockHandler, context)
  }

  try {
    return await requestFactory(context)
  } catch (error) {
    console.warn('Remote request failed, fallback to mock data.', error)
    return resolveMock(mockHandler, {
      ...context,
      error
    })
  }
}
