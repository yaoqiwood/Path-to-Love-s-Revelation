const API_PREFIX = '/api'

function withPrefix(path) {
  return `${API_PREFIX}${path}`
}

export const apiUrls = {
  files: {
    upload: () => withPrefix('/files/upload')
  },
  personnel: {
    systemConfig: () => withPrefix('/personnel/system-config'),
    loginProfiles: () => withPrefix('/personnel/login-profiles'),
    loginProfile: () => withPrefix('/personnel/login-profile'),
    login: () => withPrefix('/personnel/login'),
    searchNames: () => withPrefix('/personnel/search-names'),
    list: () => withPrefix('/personnel/list'),
    create: () => withPrefix('/personnel'),
    byId: (id) => withPrefix(`/personnel/${id}`),
    resetAllPasscodes: () => withPrefix('/personnel/reset-passcodes'),
    importExcel: () => withPrefix('/personnel/import'),
    upsertByUser: () => withPrefix('/personnel/upsert-by-user'),
    saveMbtiResult: (id) => withPrefix(`/personnel/${id}/mbti`),
    users: () => withPrefix('/personnel/users'),
    userCandidates: () => withPrefix('/personnel/user-candidates'),
    updateUserRole: (id) => withPrefix(`/personnel/${id}/user-role`),
    updatePrivateMessageQuota: (id) => withPrefix(`/personnel/${id}/private-message-quota`),
    heartHome: (personnelId) => withPrefix(`/personnel/${personnelId}/heart-home`),
    heartInbox: (personnelId) => withPrefix(`/personnel/${personnelId}/heart-inbox`),
    heartState: (personnelId) => withPrefix(`/personnel/${personnelId}/heart-state`),
    heartMessages: (personnelId) => withPrefix(`/personnel/${personnelId}/heart-messages`),
    heartPriorityBoard: (personnelId) => withPrefix(`/personnel/${personnelId}/heart-priority-board`),
    submitHeartPriorityBoard: (personnelId) =>
      withPrefix(`/personnel/${personnelId}/heart-priority-board/submit`)
  },
  heartMessages: {
    candidates: () => withPrefix('/heart-messages/candidates'),
    list: () => withPrefix('/heart-messages'),
    create: () => withPrefix('/heart-messages'),
    byId: (id) => withPrefix(`/heart-messages/${id}`)
  },
  intent: {
    rankings: () => withPrefix('/intent/rankings'),
    weightedRankings: () => withPrefix('/intent/rankings/weighted')
  }
}
