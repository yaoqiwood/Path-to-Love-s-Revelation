import { createRouter, createWebHistory } from 'vue-router'
import { app } from '@/platform/app-bridge'
import {
  ADMIN_LOGIN_PATH,
  USER_LOGIN_PATH,
  consumePostLoginHandoff,
  resolveLoginPathByRoutePath,
  validateStoredToken
} from '@/utils/auth-guard'

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

const PUBLIC_ROUTE_PATHS = new Set([
  '/',
  '/welcome',
  USER_LOGIN_PATH,
  ADMIN_LOGIN_PATH
])

let authAlertVisible = false
let authCheckErrorVisible = false

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
  const fallbackLoginPath = resolveLoginPathByRoutePath(to.path)

  if (to.name === 'not-found') {
    return true
  }

  if (PUBLIC_ROUTE_PATHS.has(to.path)) {
    return true
  }

  if (consumePostLoginHandoff(to.path)) {
    return true
  }

  try {
    const validatedUser = await validateStoredToken()
    if (validatedUser) {
      return true
    }
  } catch (error) {
    if (authCheckErrorVisible) {
      return false
    }

    authCheckErrorVisible = true
    try {
      await app.showModal({
        title: '提示',
        content: error?.message || '登录状态校验失败，请稍后重试。',
        showCancel: false,
        confirmText: '确定'
      })
    } finally {
      authCheckErrorVisible = false
    }

    return false
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
      content: '登录状态已失效，请重新登录。',
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
