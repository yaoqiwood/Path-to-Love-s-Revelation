import { http } from './request'
import type { PageParams, PageResult } from './system'

// ==================== Types ====================

export interface Participant {
    id: number
    participant_name: string
    permanent_token: string
    gender: number
    age?: number | null
    mbti?: string | null
    hometown?: string | null
    current_residence?: string | null
    create_time: string
    update_time?: string | null
}

export interface ParticipantCreate {
    participant_name: string
    permanent_token?: string  // 可选，后端自动生成
    gender: number
    age?: number | null
    mbti?: string | null
    hometown?: string | null
    current_residence?: string | null
}

export interface ParticipantUpdate {
    participant_name?: string
    permanent_token?: string
    gender?: number
    age?: number | null
    mbti?: string | null
    hometown?: string | null
    current_residence?: string | null
}

// ==================== Participant API ====================

export const participantApi = {
    /** 通过永久Token登录（无需认证） */
    loginByToken(permanent_token: string) {
        return http.post<{ access_token: string; token_type: string }>('/participants/login', { permanent_token })
    },
    list(params: PageParams) {
        return http.get<PageResult<Participant>>('/participants/', { params })
    },
    detail(id: number) {
        return http.get<Participant>(`/participants/${id}`)
    },
    getByToken(token: string) {
        return http.get<Participant>(`/participants/token/${token}`)
    },
    create(data: ParticipantCreate) {
        return http.post<Participant>('/participants/', data)
    },
    update(id: number, data: ParticipantUpdate) {
        return http.put<Participant>(`/participants/${id}`, data)
    },
    delete(id: number) {
        return http.delete(`/participants/${id}`)
    }
}
