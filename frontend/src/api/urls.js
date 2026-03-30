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
    currentLoginOpenIds: () => withPrefix('/personnel/current-login-openids'),
    byWxOpenid: () => withPrefix('/personnel/by-wx-openid'),
    loginProfiles: () => withPrefix('/personnel/login-profiles'),
    loginProfile: () => withPrefix('/personnel/login-profile'),
    searchNames: () => withPrefix('/personnel/search-names'),
    list: () => withPrefix('/personnel/list'),
    create: () => withPrefix('/personnel'),
    byId: (id) => withPrefix(`/personnel/${id}`),
    bindLoginWechatId: (id) => withPrefix(`/personnel/${id}/wechat-id`),
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
    heartMessages: (personnelId) => withPrefix(`/personnel/${personnelId}/heart-messages`)
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
