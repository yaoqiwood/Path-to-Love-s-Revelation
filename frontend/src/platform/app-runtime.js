import { getSelectedFile } from '@/platform/file-registry'
import { http, shouldUseMock, unwrapResponse } from '@/api/http'
import { apiUrls } from '@/api/urls'

const SESSION_KEY = 'app-auth-session'

function createEmptySession() {
  return {
    uid: '',
    token: '',
    tokenExpired: 0,
    userInfo: {}
  }
}

export function getCurrentUserInfo() {
  const rawValue = localStorage.getItem(SESSION_KEY)
  if (!rawValue) {
    return createEmptySession()
  }

  try {
    return JSON.parse(rawValue)
  } catch (error) {
    console.warn('Failed to parse app-auth-session.', error)
    return createEmptySession()
  }
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
