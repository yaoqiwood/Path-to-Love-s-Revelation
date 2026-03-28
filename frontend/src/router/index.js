import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/pages/index/index'
  },
  {
    path: '/pages/index/index',
    component: () => import('@/pages/index/index.vue')
  },
  {
    path: '/pages/index/service',
    component: () => import('@/pages/index/service.vue')
  },
  {
    path: '/pages/user/helper',
    component: () => import('@/pages/user/helper.vue')
  },
  {
    path: '/pages/feed/entry',
    component: () => import('@/pages/feed/entry.vue')
  },
  {
    path: '/pkg/guide/hub',
    component: () => import('@/pages/guide/hub.vue')
  },
  {
    path: '/pkg/guide/panel',
    component: () => import('@/pages/guide/panel.vue')
  },
  {
    path: '/pkg/guide/roster',
    component: () => import('@/pages/guide/roster.vue')
  },
  {
    path: '/pkg/guide/insight',
    component: () => import('@/pages/guide/insight.vue')
  },
  {
    path: '/pkg/guide/relay',
    component: () => import('@/pages/guide/relay.vue')
  },
  {
    path: '/pkg/guide/intent',
    component: () => import('@/pages/guide/intent.vue')
  },
  {
    path: '/pkg/guide/detail',
    component: () => import('@/pages/guide/detail.vue')
  },
  {
    path: '/pages/mbti-home/home',
    redirect: '/pages/index/service'
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
