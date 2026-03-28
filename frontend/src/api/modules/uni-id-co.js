function createMockUserInfo() {
  return {
    _id: 'mock-web-user',
    nickname: 'Web 访客',
    avatar: '',
    wx_openid: {
      web: 'mock-web-openid'
    },
    wx_unionid: 'mock-web-unionid'
  }
}

function saveSession(payload) {
  localStorage.setItem('app-auth-session', JSON.stringify(payload))
  localStorage.setItem('uni-id-pages-userInfo', JSON.stringify(payload.userInfo || {}))
}

export const uniIdCoService = {
  async loginByWeixin() {
    const userInfo = createMockUserInfo()
    const payload = {
      uid: userInfo._id,
      token: `mock-token-${Date.now()}`,
      tokenExpired: Date.now() + 7 * 24 * 60 * 60 * 1000,
      userInfo
    }

    saveSession(payload)
    return payload
  }
}
