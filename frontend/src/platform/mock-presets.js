import { getPersonnelById, getPersonnelList } from '@/api/modules/personnel-user'

const PROFILE_KEY = 'mbtiPersonnelProfile'
const SESSION_KEY = 'app-auth-session'
const LEGACY_USER_KEY = 'uni-id-pages-userInfo'
const SYSTEM_CONFIG_KEY = 'mock-db-system-config'

function clone(value) {
  return JSON.parse(JSON.stringify(value))
}

function buildStoredProfile(record = {}) {
  return {
    ...clone(record),
    id: record._id || '',
    personnel_id: record._id || '',
    person_id: record.person_id || '',
    user_role: Number(record.user_role) || 0,
    cached_at: Date.now()
  }
}

function buildSession(record = {}) {  const avatar = record.personal_photo || ''
  const userId = record.user_id || `mock-user-${record.person_id || 'guest'}`

  return {
    uid: userId,
    token: `mock-token-${record.person_id || 'guest'}`,
    tokenExpired: Date.now() + 7 * 24 * 60 * 60 * 1000,
    userInfo: {
      _id: userId,
      nickname: record.nickname || record.name || 'Mock 用户',
      avatar,
      avatar_file: avatar,
    }
  }
}

function writeJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value))
}

export function ensureMockBootstrap() {
  if (!localStorage.getItem(SYSTEM_CONFIG_KEY)) {
    writeJson(SYSTEM_CONFIG_KEY, {
      helper_page_review_mode: true,
      enable_heart_chat_page: true
    })
  }

  getPersonnelList()
}

export function clearMockPreset() {
  localStorage.removeItem(PROFILE_KEY)
  localStorage.removeItem(SESSION_KEY)
  localStorage.removeItem(LEGACY_USER_KEY)
}

export function applyMockPreset(preset = 'guest') {
  ensureMockBootstrap()

  if (preset === 'guest') {
    clearMockPreset()
    return null
  }

  const presetMap = {
    participant: 'personnel-101',
    user: 'personnel-102',
    coworker: 'personnel-103',
    admin: 'personnel-104'
  }

  const record = getPersonnelById(presetMap[preset])
  if (!record) {
    clearMockPreset()
    return null
  }

  writeJson(PROFILE_KEY, buildStoredProfile(record))
  writeJson(SESSION_KEY, buildSession(record))
  writeJson(LEGACY_USER_KEY, buildSession(record).userInfo)

  return record
}

export function applyMockPersonnelLogin(record = {}) {
  ensureMockBootstrap()

  if (!record || !record._id) {
    clearMockPreset()
    return null
  }

  const normalizedRecord = {
    ...record,
    user_id: record.user_id || `mock-user-${record.person_id || 'guest'}`,
  }

  const session = buildSession(normalizedRecord)
  writeJson(PROFILE_KEY, buildStoredProfile(normalizedRecord))
  writeJson(SESSION_KEY, session)
  writeJson(LEGACY_USER_KEY, session.userInfo)

  return normalizedRecord
}

export function getMockOverview() {
  ensureMockBootstrap()
  const list = getPersonnelList().filter((item) => !item.is_deleted)
  return {
    total: list.length,
    participants: list.filter((item) => Number(item.user_role) === 0).length,
    coworkers: list.filter((item) => Number(item.user_role) === 1).length,
    users: list.filter((item) => Number(item.user_role) === 2).length,
    admins: list.filter((item) => Number(item.user_role) === 3).length,
    approved: list.filter((item) => item.review_status === 'approved').length
  }
}
