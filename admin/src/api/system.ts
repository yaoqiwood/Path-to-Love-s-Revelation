import { http } from './request'

// ==================== Types ====================

export interface PageParams {
    page: number
    page_size: number
    [key: string]: any
}

export interface PageResult<T> {
    total: number
    items: T[]
}

export interface User {
    id: number
    username: string
    nickname: string
    email?: string
    avatar?: string
    user_code?: string
    feishu_id?: string
    enable_status: number
    create_time: string
    last_login_time?: string
    roles?: Role[]
}

export interface Role {
    id: number
    name: string
    code: string
    sort: number
    enable_status: number
    remark?: string
    create_time: string
}

export interface Menu {
    id: number
    pid: number
    menu_type: 'M' | 'C' | 'A'
    menu_name: string
    menu_icon?: string
    menu_sort: number
    perms?: string
    paths?: string
    component?: string
    selected?: string
    params?: string
    cache_status: number
    show_status: number
    enable_status: number
    create_time?: string
    children?: Menu[]
}

export interface UserInfo {
    user: User
    roles: string[]
    perms: string[]
}

// ==================== Auth API ====================

export const authApi = {
    login(data: any) {
        return http.post<{ access_token: string; token_type: string }>('/users/login', data)
    },
    register(data: any) {
        return http.post('/users/register', data)
    },
    logout() {
        return http.post('/users/logout')
    },
    getUserInfo() {
        return http.get<UserInfo>('/users/info')
    },
    updateProfile(id: number, data: any) {
        return http.put(`/users/${id}`, data)
    },
    getRouters() {
        return http.get<any[]>('/users/routers')
    }
}

// ==================== User API ====================

export const userApi = {
    list(params: PageParams) {
        return http.get<PageResult<User>>('/users/', { params })
    },
    detail(id: number) {
        return http.get<User>(`/users/${id}`)
    },
    create(data: any) {
        return http.post<User>('/users/', data)
    },
    update(id: number, data: any) {
        return http.put<User>(`/users/${id}`, data)
    },
    delete(id: number) {
        return http.delete(`/users/${id}`)
    },
    resetPassword(id: number, password: string) {
        return http.put(`/users/${id}/password`, { password })
    },
    changePassword(data: any) {
        return http.post('/users/password', data)
    }
}

// ==================== Role API (Mocked for now as backend pending, but standard structure) ====================

export const roleApi = {
    list(params?: any) {
        // Assuming /roles endpoint will exist
        return http.get<PageResult<Role>>('/roles/', { params })
    },
    detail(id: number) {
        return http.get<Role>(`/roles/${id}`)
    },
    create(data: any) {
        return http.post<Role>('/roles/', data)
    },
    update(id: number, data: any) {
        return http.put<Role>(`/roles/${id}`, data)
    },
    delete(id: number) {
        return http.delete(`/roles/${id}`)
    },
    // Get all roles for selection
    getAll() {
        return http.get<Role[]>('/roles/all')
    },
    // Get menu IDs assigned to a role
    getMenus(roleId: number) {
        return http.get<number[]>(`/roles/${roleId}/menus`)
    },
    // Set permissions (menus) for a role
    setMenus(roleId: number, menuIds: number[]) {
        return http.put(`/roles/${roleId}/menus`, { menu_ids: menuIds })
    }
}

// ==================== Menu API (Mocked for now) ====================

export const menuApi = {
    list(params?: any) {
        return http.get<Menu[]>('/menus/', { params })
    },
    detail(id: number) {
        return http.get<Menu>(`/menus/${id}`)
    },
    create(data: any) {
        return http.post<Menu>('/menus/', data)
    },
    update(id: number, data: any) {
        return http.put<Menu>(`/menus/${id}`, data)
    },
    delete(id: number) {
        return http.delete(`/menus/${id}`)
    },
    // Get menu tree options
    getTree() {
        return http.get<Menu[]>('/menus/tree')
    }
}

// ==================== System Log API ====================

export interface SystemLog {
    id: number
    user_id: number
    username?: string
    title: string
    business_type: number
    url: string
    ip: string
    location?: string
    method: string
    request_method: string
    operator_type: number
    param: string
    result: string
    status: number
    error?: string
    cost_time: number
    create_time: string
}

export const systemLogApi = {
    list(params: PageParams) {
        return http.get<PageResult<SystemLog>>('/system-logs/', { params })
    }
}
