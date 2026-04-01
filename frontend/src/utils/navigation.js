import { app } from '@/platform/app-bridge'

export function canGoBack() {
  return typeof window !== 'undefined' && window.history.length > 1
}

export function goBackOrReplace(fallbackUrl) {
  if (canGoBack()) {
    app.navigateBack({ delta: 1 })
    return
  }

  app.reLaunch({ url: fallbackUrl })
}
