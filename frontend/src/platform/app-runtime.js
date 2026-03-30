import { getSelectedFile } from '@/platform/file-registry'
import { getAuthStorageValue, AUTH_STORAGE_KEYS } from '@/platform/auth-storage'
import { http, shouldUseMock, unwrapResponse } from '@/api/http'
import { apiUrls } from '@/api/urls'

const SESSION_KEY = AUTH_STORAGE_KEYS.session

function createEmptySession() {
  return {
    uid: '',
    token: '',
    tokenExpired: 0,
    userInfo: {}
  }
}

export function getCurrentUserInfo() {
  const sessionValue = getAuthStorageValue(SESSION_KEY)
  if (!sessionValue || typeof sessionValue !== 'object') {
    return createEmptySession()
  }

  return sessionValue
}

export async function uploadAppFile({ filePath, cloudPath } = {}) {
  if (!filePath) {
    throw new Error('缺少待上传文件路径')
  }

  if (shouldUseMock) {
    return {
      fileID: filePath,
      cloudPath
    }
  }

  const selectedFile = getSelectedFile(filePath)
  const formData = new FormData()
  if (selectedFile) {
    formData.append('file', selectedFile, selectedFile.name)
  } else {
    formData.append('filePath', filePath)
  }
  formData.append('cloudPath', cloudPath || '')

  return unwrapResponse(
    await http.post(apiUrls.files.upload(), formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  )
}