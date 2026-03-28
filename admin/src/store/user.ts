// 用户状态管理

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type User } from '@/api/system'
import type { LoginForm, RegisterForm } from '@/types'
import { useAppStore } from './app'

export const useUserStore = defineStore('user', () => {
    // 状态
    const token = ref<string | null>(localStorage.getItem('token'))
    const user = ref<User | null>(null)
    const roles = ref<string[]>([])
    const permissions = ref<string[]>([])
    const menus = ref<any[]>([])
    const loading = ref(false)

    // 计算属性
    const isLoggedIn = computed(() => !!token.value)
    const isAdmin = computed(() => roles.value.includes('admin'))

    // 设置Token
    function setToken(newToken: string | null) {
        token.value = newToken
        if (newToken) {
            localStorage.setItem('token', newToken)
        } else {
            localStorage.removeItem('token')
        }
    }

    // 登录
    async function login(form: LoginForm) {
        loading.value = true
        try {
            const response = await authApi.login(form)
            setToken(response.access_token)
            await fetchCurrentUser()
            return true
        } catch (error) {
            return false
        } finally {
            loading.value = false
        }
    }

    // 注册
    async function register(form: RegisterForm) {
        loading.value = true
        try {
            await authApi.register(form)
            // 注册成功后自动登录
            return await login({
                username: form.username,
                password: form.password
            })
        } catch (error) {
            return false
        } finally {
            loading.value = false
        }
    }

    // 获取当前用户信息
    async function fetchCurrentUser() {
        if (!token.value) return null

        try {
            const userInfo = await authApi.getUserInfo()
            if (!userInfo || !userInfo.user) {
                throw new Error('User info response invalid')
            }

            user.value = userInfo.user
            roles.value = userInfo.roles
            permissions.value = userInfo.perms

            // Fetch menus
            try {
                const menuData = await authApi.getRouters()
                menus.value = menuData
            } catch (e) {
                console.error('Failed to fetch menus', e)
            }

            // Init app configs
            try {
                const appStore = useAppStore()
                appStore.initConfigs()
            } catch (e) {
                console.error('Failed to init configs', e)
            }

            return userInfo.user
        } catch (error) {
            // Token无效，清除登录状态
            console.error('Failed to fetch user info:', error)
            logout()
            return null
        }
    }

    // 更新用户信息
    async function updateProfile(data: {
        full_name?: string
        email?: string
        avatar?: string
    }) {
        if (!user.value?.id) return false

        try {
            await authApi.updateProfile(user.value.id, data)
            await fetchCurrentUser() // Refresh info
            return true
        } catch (error) {
            return false
        }
    }

    // 登出
    function logout() {
        setToken(null)
        user.value = null
    }

    // 初始化：如果有token则获取用户信息
    async function init() {
        if (token.value) {
            await fetchCurrentUser()
        }
    }

    return {
        // 状态
        token,
        user,
        roles,
        permissions,
        menus,
        loading,
        // 计算属性
        isLoggedIn,
        isAdmin,
        // 方法
        login,
        register,
        fetchCurrentUser,
        updateProfile,
        logout,
        init,
    }
})
