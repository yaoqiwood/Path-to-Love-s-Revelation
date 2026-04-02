const explicitMockValue = String(import.meta.env.VITE_USE_MOCK || '')
  .trim()
  .toLowerCase()

const MOCK_ON_VALUES = new Set(['true', '1', 'yes', 'on'])

export const shouldUseMock = MOCK_ON_VALUES.has(explicitMockValue)

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

  if (!hasMockHandler(mockHandler) || !shouldUseMock) {
    return requestFactory(context)
  }

  return resolveMock(mockHandler, context)
}
