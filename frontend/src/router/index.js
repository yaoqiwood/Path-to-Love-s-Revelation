import { createRouter, createWebHistory } from 'vue-router'
import { app } from '@/platform/app-bridge'

const routes = [
  {
    path: '/',
    component: () => import('@/pages/welcome/love-path-welcome.vue')
  },
  {
    path: '/welcome',
    component: () => import('@/pages/welcome/love-path-welcome.vue')
  },
  {
    path: '/pages/index/index',
    component: () => import('@/pages/index/profile-route-gateway.vue')
  },
  {
    path: '/pages/index/home',
    component: () => import('@/pages/index/love-feature-home.vue')
  },
  {
    path: '/pages/index/login-home',
    component: () => import('@/pages/index/love-login-home.vue')
  },
  {
    path: '/pages/index/admin-login-home',
    component: () => import('@/pages/index/admin-login-home.vue')
  },
  {
    path: '/pages/index/heart-priority-board',
    component: () => import('@/pages/index/heart-priority-board.vue')
  },
  {
    path: '/pages/user/helper',
    component: () => import('@/pages/user/test-access-entry.vue')
  },
  {
    path: '/pages/feed/entry',
    component: () => import('@/pages/feed/mbti-test-session.vue')
  },
  {
    path: '/api_tester',
    alias: '/api-tester',
    component: () => import('@/pages/tools/api-tester.vue')
  },
  {
    path: '/pkg/guide/hub',
    component: () => import('@/pages/guide/admin-navigation-hub.vue')
  },
  {
    path: '/pkg/guide/panel',
    component: () => import('@/pages/guide/admin-user-management.vue')
  },
  {
    path: '/pkg/guide/roster',
    component: () => import('@/pages/guide/admin-personnel-management.vue')
  },
  {
    path: '/pkg/guide/insight',
    component: () => import('@/pages/guide/admin-mbti-pairing.vue')
  },
  {
    path: '/pkg/guide/relay',
    component: () => import('@/pages/guide/admin-heart-message-management.vue')
  },
  {
    path: '/pkg/guide/intent',
    component: () => import('@/pages/guide/admin-intent-ranking.vue')
  },
  {
    path: '/pkg/guide/detail',
    component: () => import('@/pages/guide/user-message-center.vue')
  },
  {
    path: '/pages/mbti-home/home',
    redirect: '/pages/index/login-home'
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/pages/system/not-found.vue')
  }
]

const LOGIN_PAGE_PATH = '/pages/index/login-home'
const ADMIN_LOGIN_PAGE_PATH = '/pages/index/admin-login-home'
const API_TESTER_PATH = '/api_tester'
const API_TESTER_ALIAS_PATH = '/api-tester'
const PUBLIC_ROUTE_PATHS = new Set([
  '/',
  '/welcome',
  LOGIN_PAGE_PATH,
  ADMIN_LOGIN_PAGE_PATH,
  API_TESTER_PATH,
  API_TESTER_ALIAS_PATH
])
const LOGIN_PROFILE_COOKIE_KEY = 'mbtiPersonnelProfile'

let authAlertVisible = false

function readCookieRaw(name) {
  if (typeof document === 'undefined') {
    return ''
  }

  const prefix = `${encodeURIComponent(String(name))}=`
  const segments = String(document.cookie || '').split(';')
  for (let index = 0; index < segments.length; index += 1) {
    const item = segments[index].trim()
    if (item.startsWith(prefix)) {
      return decodeURIComponent(item.slice(prefix.length))
    }
  }

  return ''
}

function hasLoginProfileCookie() {
  const rawValue = readCookieRaw(LOGIN_PROFILE_COOKIE_KEY)
  if (!rawValue) {
    return false
  }

  try {
    const profile = JSON.parse(rawValue)
    return !!(profile && typeof profile === 'object' && (profile._id || profile.id || profile.personnel_id))
  } catch (error) {
    return false
  }
}

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }

    if (to.fullPath === from.fullPath) {
      return false
    }

    return { top: 0 }
  }
})

router.beforeEach(async (to) => {
  const fallbackLoginPath = to.path.startsWith('/pkg/guide/') ? ADMIN_LOGIN_PAGE_PATH : LOGIN_PAGE_PATH

  if (to.name === 'not-found') {
    return true
  }

  if (PUBLIC_ROUTE_PATHS.has(to.path)) {
    return true
  }

  if (hasLoginProfileCookie()) {
    return true
  }

  if (authAlertVisible) {
    return {
      path: fallbackLoginPath,
      replace: true
    }
  }

  authAlertVisible = true
  try {
    await app.showModal({
      title: '提示',
      content: '未检测到用户信息，请先登录。',
      showCancel: false,
      confirmText: '确定'
    })
  } finally {
    authAlertVisible = false
  }

  return {
    path: fallbackLoginPath,
    replace: true
  }
})

export default router
