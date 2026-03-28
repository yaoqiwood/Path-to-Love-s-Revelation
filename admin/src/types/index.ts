// TypeScript类型定义

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

// ==================== 项目相关 ====================
export interface Project {
    id: number
    name: string
    source: string // new
    description?: string
    cover_url?: string // new
    status: ProjectStatus
    need_lang: string[] // new
    deadline?: string
    created_at: string
    updated_at: string
    created_by?: number
    updated_by?: number
    // 统计
    task_count: number
    material_count: number
    script_count: number
    export_count: number
    created_by_name?: string
    updater_name?: string
}

export type ProjectStatus = 'PLANNING' | 'PRODUCING' | 'LAUNCHED' | 'ARCHIVED'

export interface ProjectForm {
    name: string
    source: string
    description?: string
    cover_url?: string
    status: ProjectStatus
    need_lang: string[]
    deadline?: string
}

export interface AIPreferences {
    tone?: 'emotional' | 'rational'
    style?: 'conflict' | 'storytelling'
    default_duration?: number
}

export interface PlatformProfile {
    id: number
    platform: string
    display_name: string
    video_config: VideoConfig
    text_config: TextConfig
    rules: RulesConfig
    is_active: boolean
}

export interface VideoConfig {
    ratio: string
    max_duration: number
    safe_area: {
        top: number
        bottom: number
    }
}

export interface TextConfig {
    max_length: number
    max_lines: number
}

export interface RulesConfig {
    allow_exaggeration: boolean
    restricted_words: string[]
}

export interface ProjectProgress {
    total_tasks: number
    dispatched_tasks: number
    completed_tasks: number
    in_progress_tasks: number
    todo_tasks: number
    creative_results: number
    progress_percentage: number
}

// ==================== 任务相关 ====================
export interface Task {
    id: number
    title: string
    description?: string
    type: TaskType
    status: TaskStatus
    priority: TaskPriority
    project_id: number
    assignee_id?: number
    parent_task_id?: number
    deadline?: string
    started_at?: string
    completed_at?: string
    created_at: string
    sort_order: number
}

export type TaskType = 'creative' | 'collect' | 'edit' | 'review' | 'export'
export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'completed' | 'cancelled'
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface TaskForm {
    title: string
    description?: string
    type?: TaskType
    priority?: TaskPriority
    project_id: number
    assignee_id?: number
    deadline?: string
}

export interface TaskBoard {
    columns: TaskBoardColumn[]
}

export interface TaskBoardColumn {
    status: TaskStatus
    tasks: Task[]
}

export interface Tag {
    id: number
    name: string
    created_by?: number
    updated_by?: number
    created_at?: string
    updated_at?: string
}

// ==================== 素材相关 ====================
export interface Material {
    id: number
    name: string
    description?: string
    file_type: MaterialType
    source: MaterialSource
    file_path: string
    thumbnail_path?: string
    file_size?: number
    mime_type?: string
    file_metadata?: Record<string, any>
    tags: Tag[]
    category?: string
    project_id: number
    created_at: string
    original_filename?: string
    created_by: number
    creator_name?: string
    visibility?: MaterialVisibility
}

export type MaterialType = 'image' | 'video' | 'audio' | 'text'
export type MaterialSource = 'upload' | 'ai_generated' | 'template' | 'external'
export type MaterialVisibility = 'public' | 'private'

export interface MaterialFilter {
    file_type?: MaterialType
    source?: string
    category?: string
    search?: string
    created_by?: number
    tag_ids?: string
    project_id?: number
}

export interface AIGenerateRequest {
    project_id: number
    prompt: string
    negative_prompt?: string
    style?: string
    width?: number
    height?: number
    num_images?: number
}

export interface MaterialStats {
    total: number
    by_type: Record<MaterialType, number>
    total_size: number
}

// ==================== 模板相关 ====================
export interface Template {
    id: number
    name: string
    description?: string
    type: TemplateType
    category?: TemplateCategory
    config: TemplateConfig
    preview_image?: string
    preview_video?: string
    default_width: number
    default_height: number
    default_fps: number
    default_duration?: number
    is_public: boolean
    is_active: boolean
    version: string
    usage_count: number
    created_at: string
    updated_at: string
}

export type TemplateType = 'video_short' | 'video_long' | 'image_single' | 'image_carousel' | 'dynamic_poster'
export type TemplateCategory = 'product' | 'promotion' | 'brand' | 'event' | 'testimonial' | 'tutorial'

export interface TemplateConfig {
    slots: TemplateSlot[]
    variables: TemplateVariable[]
    steps: TemplateStep[]
    output: TemplateOutput
}

export interface TemplateSlot {
    id: string
    type: string
    required: boolean
    description?: string
}

export interface TemplateVariable {
    name: string
    type: string
    default?: string
    max_length?: number
}

export interface TemplateStep {
    action: string
    [key: string]: any
}

export interface TemplateOutput {
    format: string
    codec?: string
    quality?: string
}

export interface TemplateApplyRequest {
    material_ids: number[]
    variables: Record<string, any>
    output_format?: string
    output_width?: number
    output_height?: number
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

export interface MaterialListResponse extends PaginatedResponse<Material> {
    creators: Creator[]
    categories: string[]
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
