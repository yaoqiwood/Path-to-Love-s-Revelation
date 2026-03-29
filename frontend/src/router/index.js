import { createRouter, createWebHistory } from 'vue-router'

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
  }
]

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

export default router
