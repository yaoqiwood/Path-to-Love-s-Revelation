// API请求封装

import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { apiBaseURL, apiTimeout } from '@/config'

// 创建axios实例
const request: AxiosInstance = axios.create({
    baseURL: apiBaseURL,
    timeout: apiTimeout,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
request.interceptors.request.use(
    (config) => {
        const userStore = useUserStore()

        // 添加认证令牌
        if (userStore.token) {
            config.headers.Authorization = `Bearer ${userStore.token}`
        }

        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// 响应拦截器
request.interceptors.response.use(
    (response: AxiosResponse) => {
        return response.data
    },
    (error) => {
        const userStore = useUserStore()

        if (error.response) {
            const { status, data } = error.response

            switch (status) {
                case 401:
                    if (data?.code === 'INVALID_CREDENTIALS') {
                        // Token 过期 → 弹提示并跳登录
                        userStore.logout()
                        ElMessage({
                            type: 'error',
                            message: data?.message || '登录已过期，请重新登录',
                            duration: 1500,
                            onClose: () => {
                                window.location.href = '/login'
                            }
                        })
                    } else {
                        // 密码错误等
                        ElMessage.error(data?.message || '认证失败')
                    }
                    break
                case 403:
                    ElMessage.error(data?.message || '权限不足')
                    break
                case 404:
                    ElMessage.error(data?.message || '资源不存在')
                    break
                case 422: {
                    // 参数验证错误：从 detail 数组提取可读错误信息
                    let msg = data?.message || '请求参数验证失败'
                    if (Array.isArray(data?.detail)) {
                        const messages = data.detail.map(
                            (e: any) => e.msg || JSON.stringify(e)
                        )
                        msg = messages.join('; ')
                    }
                    ElMessage.error(msg)
                    break
                }
                case 500:
                    ElMessage.error(data?.message || '服务器错误')
                    break
                default:
                    ElMessage.error(data?.message || '请求失败')
            }
        } else if (error.request) {
            ElMessage.error('网络错误，请检查网络连接')
        }

        return Promise.reject(error)
    }
)

// 封装请求方法
export const http = {
    get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
        return request.get(url, config)
    },

    post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
        return request.post(url, data, config)
    },

    put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
        return request.put(url, data, config)
    },

    patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
        return request.patch(url, data, config)
    },

    delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
        return request.delete(url, config)
    },

    upload<T = any>(url: string, formData: FormData, onProgress?: (percent: number) => void): Promise<T> {
        return request.post(url, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
                if (onProgress && progressEvent.total) {
                    const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                    onProgress(percent)
                }
            }
        })
    }
}

export default request
