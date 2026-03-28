import { createUniBridge } from '@/platform/uni-compat'

const uniBridge = createUniBridge()

globalThis.__APP_UNI__ = uniBridge
globalThis.__APP_GET_CURRENT_PAGES__ = function getCurrentPagesCompat() {
  const historyLength = window.history.length || 1
  return Array.from({ length: historyLength }, (_, index) => ({
    route: index === historyLength - 1 ? window.location.pathname : ''
  }))
}
