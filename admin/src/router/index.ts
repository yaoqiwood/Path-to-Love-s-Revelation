// Vue Router配置

import { createRouter, createWebHistory, RouterView } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { h } from 'vue'
import { useUserStore } from '@/store/user'

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        redirect: '/dashboard'
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Login.vue'),
        meta: { guest: true }
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/Register.vue'),
        meta: { guest: true }
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { requiresAuth: true }
    },
    // System Management
    {
        path: '/system',
        name: 'System',
        component: { render: () => h(RouterView) },
        redirect: '/system/user',
        meta: { title: '系统管理', icon: 'Setting', requiresAuth: true },
        children: [
            {
                path: 'user', // /system/user
                name: 'User',
                component: () => import('@/views/system/user/index.vue'),
                meta: { title: '用户管理', icon: 'User', requiresAuth: true }
            },
            {
                path: 'role', // /system/role
                name: 'Role',
                component: () => import('@/views/system/role/index.vue'),
                meta: { title: '角色管理', icon: 'Avatar', requiresAuth: true }
            },
            {
                path: 'menu', // /system/menu
                name: 'Menu',
                component: () => import('@/views/system/menu/index.vue'),
                meta: { title: '菜单管理', icon: 'Menu', requiresAuth: true }
            },
            {
                path: 'log', // /system/log
                name: 'SystemLog',
                component: () => import('@/views/system/log/index.vue'),
                meta: { title: '操作日志', icon: 'Document', requiresAuth: true }
            },
            {
                path: 'configs', // /system/configs
                name: 'Configs',
                component: () => import('@/views/system/Configs.vue'),
                meta: { title: '系统配置', icon: 'Setting', requiresAuth: true }
            }
        ]
    },
    // Activity Management
    {
        path: '/activity',
        name: 'Activity',
        component: { render: () => h(RouterView) },
        redirect: '/activity/participant',
        meta: { title: '活动管理', icon: 'Star', requiresAuth: true },
        children: [
            {
                path: 'participant', // /activity/participant
                name: 'Participant',
                component: () => import('@/views/activity/participant/index.vue'),
                meta: { title: '参与者管理', icon: 'User', requiresAuth: true }
            }
        ]
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('@/views/NotFound.vue')
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 导航守卫
router.beforeEach(async (to, _from, next) => {
    const userStore = useUserStore()

    // 如果需要认证
    if (to.meta.requiresAuth) {
        if (!userStore.isLoggedIn) {
            return next({ name: 'Login', query: { redirect: to.fullPath } })
        }

        // 如果有token但没有用户信息，尝试获取
        if (!userStore.user) {
            await userStore.fetchCurrentUser()
            if (!userStore.user) {
                return next({ name: 'Login' })
            }
        }
    }

    // 如果是访客页面（登录/注册）且已登录，重定向到首页
    if (to.meta.guest && userStore.isLoggedIn) {
        return next({ name: 'Dashboard' })
    }

    next()
})

export default router
