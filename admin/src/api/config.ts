// 系统配置API

import { http } from './request'

// 类型定义
export interface AppConfig {
    id: number
    key: string
    value: any
    value_type?: string
    group?: string
    remark?: string
    is_secret: boolean
    is_active: boolean
    created_at: string
    updated_at: string
}

export interface ConfigCreate {
    key: string
    value: any
    value_type?: string
    group?: string
    remark?: string
    is_secret?: boolean
}

export interface ConfigUpdate {
    value?: any
    value_type?: string
    group?: string
    remark?: string
    is_secret?: boolean
    is_active?: boolean
}

export interface ConfigListResponse {
    items: AppConfig[]
    total: number
}

export interface ConfigValueResponse {
    key: string
    value: any
    value_type?: string
}

export interface ConfigBatchResponse {
    configs: Record<string, any>
}

export const configApi = {
    // 获取配置列表
    list(params?: {
        group?: string
        search?: string
        is_active?: boolean
        include_secrets?: boolean
    }): Promise<ConfigListResponse> {
        return http.get('/configs', { params })
    },

    // 获取配置分组
    listGroups(): Promise<{ groups: string[] }> {
        return http.get('/configs/groups')
    },

    // 通过键获取配置
    getByKey(key: string, deserialize?: boolean): Promise<ConfigValueResponse> {
        return http.get(`/configs/key/${key}`, { params: { deserialize } })
    },

    // 批量获取配置
    getBatch(keys: string[]): Promise<ConfigBatchResponse> {
        return http.post('/configs/batch', { keys })
    },

    // 获取配置详情
    get(id: number): Promise<AppConfig> {
        return http.get(`/configs/${id}`)
    },

    // 创建配置
    create(data: ConfigCreate): Promise<AppConfig> {
        return http.post('/configs', data)
    },

    // 更新配置
    update(id: number, data: ConfigUpdate): Promise<AppConfig> {
        return http.put(`/configs/${id}`, data)
    },

    // 通过键更新配置
    updateByKey(key: string, data: ConfigUpdate): Promise<AppConfig> {
        return http.put(`/configs/key/${key}`, data)
    },

    // 删除配置
    delete(id: number): Promise<void> {
        return http.delete(`/configs/${id}`)
    },

    // ========== 缓存管理 ==========

    // 刷新缓存
    refreshCache(params?: {
        key?: string
        group?: string
    }): Promise<{ message: string }> {
        return http.post('/configs/cache/refresh', params || {})
    },

    // 获取缓存统计
    getCacheStats(): Promise<{
        total_cached: number
        cache_prefix: string
        default_ttl: number
    }> {
        return http.get('/configs/cache/stats')
    }
}
