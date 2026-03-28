/**
 * API 端点配置
 * 集中管理所有 API 端点路径
 */

export const API_ENDPOINTS = {
    // 用户相关
    AUTH: {
        LOGIN: '/users/login',
        LOGOUT: '/users/logout',
        REGISTER: '/users/register',
        PROFILE: '/users/me',
        UPDATE_PROFILE: '/users/me',
        CHANGE_PASSWORD: '/users/me/password'
    },

    // 项目相关
    PROJECTS: {
        LIST: '/projects',
        DETAIL: (id: number) => `/projects/${id}`,
        CREATE: '/projects',
        UPDATE: (id: number) => `/projects/${id}`,
        DELETE: (id: number) => `/projects/${id}`,
        STATS: (id: number) => `/projects/${id}/stats`
    },

    // 任务相关
    TASKS: {
        LIST: '/tasks',
        DETAIL: (id: number) => `/tasks/${id}`,
        CREATE: '/tasks',
        UPDATE: (id: number) => `/tasks/${id}`,
        DELETE: (id: number) => `/tasks/${id}`,
        START: (id: number) => `/tasks/${id}/start`,
        PAUSE: (id: number) => `/tasks/${id}/pause`,
        COMPLETE: (id: number) => `/tasks/${id}/complete`
    },

    // 素材相关
    MATERIALS: {
        LIST: '/materials',
        DETAIL: (id: number) => `/materials/${id}`,
        CREATE: '/materials',
        UPDATE: (id: number) => `/materials/${id}`,
        DELETE: (id: number) => `/materials/${id}`,
        UPLOAD: '/materials/upload',
        BATCH_DELETE: '/materials/batch-delete'
    },

    // PSD 模板
    PSD_TEMPLATES: {
        LIST: '/psd-templates',
        DETAIL: (id: number) => `/psd-templates/${id}`,
        CREATE: '/psd-templates',
        UPDATE: (id: number) => `/psd-templates/${id}`,
        DELETE: (id: number) => `/psd-templates/${id}`,
        UPLOAD: '/psd-templates/upload'
    },

    // 字体相关
    FONTS: {
        LIST: '/fonts',
        DETAIL: (id: number) => `/fonts/${id}`,
        UPLOAD: '/fonts/upload',
        DELETE: (id: number) => `/fonts/${id}`,
    },

    // 标签相关
    TAGS: {
        LIST: '/tags',
        DETAIL: (id: number) => `/tags/${id}`,
        CREATE: '/tags',
        UPDATE: (id: number) => `/tags/${id}`,
        DELETE: (id: number) => `/tags/${id}`
    },

    // 配置相关
    CONFIGS: {
        LIST: '/configs',
        DETAIL: (id: number) => `/configs/${id}`,
        BY_KEY: (key: string) => `/configs/key/${key}`,
        CREATE: '/configs',
        UPDATE: (id: number) => `/configs/${id}`,
        DELETE: (id: number) => `/configs/${id}`,
        GROUPS: '/configs/groups',
        MODELS: '/configs/models',
        CACHE_REFRESH: '/configs/cache/refresh',
        CACHE_STATS: '/configs/cache/stats'
    }
} as const

export default API_ENDPOINTS
