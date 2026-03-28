import { reactive } from 'vue'

export const uiState = reactive({
  toasts: [],
  loading: false,
  loadingText: '处理中...',
  modal: null
})

let toastSeed = 0

export function pushToast(options = {}) {
  const title = String(options.title || options.message || '').trim()
  if (!title) {
    return
  }

  const toast = {
    id: `toast-${Date.now()}-${toastSeed += 1}`,
    title,
    icon: options.icon || 'none'
  }

  uiState.toasts.push(toast)

  const duration = Number(options.duration) || 2200
  window.setTimeout(() => {
    uiState.toasts = uiState.toasts.filter((item) => item.id !== toast.id)
  }, duration)
}

export function showLoading(options = {}) {
  uiState.loading = true
  uiState.loadingText = String(options.title || '加载中...')
}

export function hideLoading() {
  uiState.loading = false
  uiState.loadingText = '处理中...'
}

export function openModal(options = {}) {
  return new Promise((resolve) => {
    uiState.modal = {
      ...options,
      __resolve: resolve
    }
  })
}

export function resolveModalAction(confirm) {
  if (!uiState.modal) {
    return
  }

  const modal = uiState.modal
  uiState.modal = null

  const payload = {
    confirm,
    cancel: !confirm
  }

  if (typeof modal.success === 'function') {
    modal.success(payload)
  }

  modal.__resolve(payload)
}
