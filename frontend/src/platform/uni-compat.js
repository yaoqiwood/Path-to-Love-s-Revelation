import { getAppRouter } from '@/router/holder'
import { rememberSelectedFile } from '@/platform/file-registry'
import { hideLoading, openModal, pushToast, showLoading } from '@/platform/ui-state'
import { getAuthStorageValue, isAuthStorageKey, removeAuthStorageValue, setAuthStorageValue } from '@/platform/auth-storage'

function normalizePath(url = '/') {
  const value = String(url || '').trim()
  return value || '/'
}

function ensureRouter() {
  const router = getAppRouter()
  if (!router) {
    throw new Error('Router has not been registered yet.')
  }
  return router
}

function parseStoredValue(rawValue) {
  if (rawValue == null) {
    return ''
  }

  try {
    return JSON.parse(rawValue)
  } catch (error) {
    return rawValue
  }
}

function openFileDialog({ accept = '*/*', multiple = false, onResolve, onReject }) {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = accept
  input.multiple = multiple
  input.style.position = 'fixed'
  input.style.left = '-9999px'
  input.style.top = '0'

  input.addEventListener(
    'change',
    () => {
      const fileList = Array.from(input.files || [])
      document.body.removeChild(input)
      if (!fileList.length) {
        onReject({
          errMsg: 'chooseFile:fail cancel'
        })
        return
      }
      onResolve(fileList)
    },
    {
      once: true
    }
  )

  document.body.appendChild(input)
  input.click()
}

function buildChooseImageResult(fileList) {
  const tempFilePaths = fileList.map((file) => rememberSelectedFile(file))
  return {
    tempFilePaths,
    tempFiles: fileList.map((file, index) => ({
      name: file.name,
      size: file.size,
      type: file.type,
      path: tempFilePaths[index],
      tempFilePath: tempFilePaths[index]
    }))
  }
}

function buildChooseFileResult(fileList) {
  return {
    tempFiles: fileList.map((file) => {
      const path = rememberSelectedFile(file)
      return {
        name: file.name,
        size: file.size,
        type: file.type,
        path,
        tempFilePath: path,
        file
      }
    })
  }
}

function createSelectorQuery() {
  const tasks = []

  const api = {
    in() {
      return api
    },
    select(selector) {
      return {
        boundingClientRect() {
          tasks.push({
            type: 'rect',
            selector
          })
          return api
        }
      }
    },
    selectViewport() {
      return {
        scrollOffset() {
          tasks.push({
            type: 'viewport'
          })
          return api
        }
      }
    },
    exec(callback) {
      const result = tasks.map((task) => {
        if (task.type === 'viewport') {
          return {
            scrollTop: window.scrollY,
            scrollLeft: window.scrollX
          }
        }

        const element = document.querySelector(task.selector)
        if (!element) {
          return null
        }

        const rect = element.getBoundingClientRect()
        return {
          top: rect.top,
          left: rect.left,
          right: rect.right,
          bottom: rect.bottom,
          width: rect.width,
          height: rect.height
        }
      })

      if (typeof callback === 'function') {
        callback(result)
      }
    }
  }

  return api
}

export function createUniBridge() {
  return {
    showToast(options = {}) {
      pushToast(options)
    },
    showModal(options = {}) {
      return openModal(options)
    },
    showLoading(options = {}) {
      showLoading(options)
    },
    hideLoading() {
      hideLoading()
    },
    navigateTo({ url } = {}) {
      return ensureRouter().push(normalizePath(url))
    },
    reLaunch({ url } = {}) {
      return ensureRouter().replace(normalizePath(url))
    },
    navigateBack({ delta = 1 } = {}) {
      ensureRouter().go(-Math.max(1, Number(delta) || 1))
    },
    pageScrollTo({ scrollTop = 0, duration = 0 } = {}) {
      window.scrollTo({
        top: Number(scrollTop) || 0,
        behavior: duration > 0 ? 'smooth' : 'auto'
      })
    },
    setStorageSync(key, value) {
      const normalizedKey = String(key)
      if (isAuthStorageKey(normalizedKey)) {
        setAuthStorageValue(normalizedKey, value)
        return
      }

      localStorage.setItem(normalizedKey, JSON.stringify(value))
    },
    getStorageSync(key) {
      const normalizedKey = String(key)
      if (isAuthStorageKey(normalizedKey)) {
        return getAuthStorageValue(normalizedKey)
      }

      return parseStoredValue(localStorage.getItem(normalizedKey))
    },
    removeStorageSync(key) {
      const normalizedKey = String(key)
      if (isAuthStorageKey(normalizedKey)) {
        removeAuthStorageValue(normalizedKey)
        return
      }

      localStorage.removeItem(normalizedKey)
    },
    chooseImage(options = {}) {
      return new Promise((resolve, reject) => {
        openFileDialog({
          accept: 'image/*',
          multiple: Number(options.count) > 1,
          onResolve(fileList) {
            const payload = buildChooseImageResult(fileList)
            options.success?.(payload)
            resolve(payload)
          },
          onReject(error) {
            options.fail?.(error)
            reject(error)
          }
        })
      })
    },
    chooseFile(options = {}) {
      const extensions = Array.isArray(options.extension) ? options.extension : []
      const accept = extensions.length ? extensions.map((item) => `.${item}`).join(',') : '*/*'

      return new Promise((resolve, reject) => {
        openFileDialog({
          accept,
          multiple: Number(options.count) > 1,
          onResolve(fileList) {
            const payload = buildChooseFileResult(fileList)
            options.success?.(payload)
            resolve(payload)
          },
          onReject(error) {
            options.fail?.(error)
            reject(error)
          }
        })
      })
    },
    login() {
      return Promise.resolve({
        code: `mock-code-${Date.now()}`
      })
    },
    createSelectorQuery,
    onPushMessage() {},
    offPushMessage() {},
    getPushClientId(options = {}) {
      const payload = {
        cid: 'web-client'
      }
      options.success?.(payload)
      return Promise.resolve(payload)
    }
  }
}
