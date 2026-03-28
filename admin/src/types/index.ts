// TypeScript类型定义（框架基础类型）

// ==================== 用户相关 ====================
export interface User {
    id: number
    username: string
    email: string
    full_name?: string
    avatar?: string
    role: UserRole
    is_active: boolean
    created_at: string
}

export type UserRole = 'admin' | 'manager' | 'creator' | 'viewer'

export interface LoginForm {
    username: string
    password: string
}

export interface RegisterForm {
    username: string
    email: string
    password: string
    full_name?: string
}

// ==================== API响应 ====================
export interface ApiResponse<T> {
    data: T
    message?: string
}

export interface PaginatedResponse<T> {
    items: T[]
    total: number
    page: number
    page_size: number
}

export interface AsyncTaskResponse {
    task_id: string
    status: string
    message: string
}

export interface Creator {
    id: number
    username: string
}
