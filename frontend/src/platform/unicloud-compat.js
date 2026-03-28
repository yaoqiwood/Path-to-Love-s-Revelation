import { getSelectedFile } from '@/platform/file-registry'
import { http, shouldUseMock, unwrapResponse } from '@/api/http'
import { personnelUserService } from '@/api/modules/personnel-user'
import { uniIdCoService } from '@/api/modules/uni-id-co'

function getAuthSession() {
  const rawValue = localStorage.getItem('app-auth-session')
  if (!rawValue) {
    return {
      uid: '',
      token: '',
      tokenExpired: 0,
      userInfo: {}
    }
  }

  try {
    return JSON.parse(rawValue)
  } catch (error) {
    console.warn('Failed to parse app-auth-session.', error)
    return {
      uid: '',
      token: '',
      tokenExpired: 0,
      userInfo: {}
    }
  }
}

function createDatabaseCollection(collectionName) {
  const state = {
    collectionName,
    sortKey: '',
    sortDirection: 'asc',
    skipValue: 0,
    limitValue: 500
  }

  return {
    field() {
      return this
    },
    orderBy(key, direction = 'asc') {
      state.sortKey = key
      state.sortDirection = direction
      return this
    },
    skip(value) {
      state.skipValue = Number(value) || 0
      return this
    },
    limit(value) {
      state.limitValue = Number(value) || 500
      return this
    },
    async get() {
      if (state.collectionName !== 'mbti-personnel') {
        return {
          data: [],
          result: {
            data: []
          }
        }
      }

      const page = Math.floor(state.skipValue / state.limitValue) + 1
      const response = await personnelUserService.list({
        page,
        pageSize: state.limitValue,
        includeDeleted: true
      })
      let list = response.list || []

      if (state.sortKey) {
        const factor = state.sortDirection === 'desc' ? -1 : 1
        list = [...list].sort((left, right) => {
          const leftValue = left?.[state.sortKey]
          const rightValue = right?.[state.sortKey]
          if (leftValue === rightValue) {
            return 0
          }
          return leftValue > rightValue ? factor : -factor
        })
      }

      return {
        data: list,
        result: {
          data: list
        }
      }
    }
  }
}

export const uniCloudBridge = {
  importObject(name) {
    if (name === 'personnel-user') {
      return personnelUserService
    }

    if (name === 'uni-id-co') {
      return uniIdCoService
    }

    throw new Error(`Unknown cloud object: ${name}`)
  },

  getCurrentUserInfo() {
    return getAuthSession()
  },

  async uploadFile({ filePath, cloudPath } = {}) {
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
      await http.post('/api/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    )
  },

  database() {
    return {
      collection(name) {
        return createDatabaseCollection(name)
      }
    }
  }
}
