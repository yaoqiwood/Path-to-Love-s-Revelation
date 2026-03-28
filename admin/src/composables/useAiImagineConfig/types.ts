import type { InjectionKey, Ref } from 'vue'

// ==================== 常量与枚举 ====================

/** 生成模式 */
export type AiImagineMode = 'text' | 'image' | 'multi_image'

/** 生成类型（全局） */
export type AiImagineGenerateType = 'IMAGE_GEN' | 'VIDEO_GEN' | 'IMAGE_RECOGNITION' | 'TEXT_ANALYSIS'

/** 模式选项（用于 UI 渲染） */
export const AI_IMAGINE_MODE_OPTIONS: { label: string; value: AiImagineMode; icon: string }[] = [
    { label: '文本输入', value: 'text', icon: '📝' },
    { label: '图片参考', value: 'image', icon: '🖼️' },
    { label: '多图融合', value: 'multi_image', icon: '🎨' },
]

/** 默认系统提示词预设 */
export const DEFAULT_SYSTEM_PROMPTS: Record<AiImagineGenerateType, string> = {
    IMAGE_GEN: '请根据用户的描述, 输出高质量的图片',
    VIDEO_GEN: '根据用户的描述, 输出高质量的视频',
    IMAGE_RECOGNITION: '请根据用户上传的文件, 输出高质量的提示词',
    TEXT_ANALYSIS: '请根据用户的描述, 输出高质量的提示词',
}

/** 内容设定项 */
export interface ContentSetting {
    label: string
    key: string
    content: string
    placeholder?: string
}

/** 预设内容设定标签 */
export const CONTENT_SETTING_PRESETS = [
    { label: '角色形象', icon: '👤', key: 'character', placeholder: '请输入角色形象' },
    { label: '位置关系', icon: '📍', key: 'position', placeholder: '请输入位置关系' },
    { label: '画面风格', icon: '🎨', key: 'style', placeholder: '请输入画面风格' },
    { label: '场景环境', icon: '🌄', key: 'scene', placeholder: '请输入场景环境' },
    { label: '镜头景别', icon: '🎥', key: 'camera', placeholder: '请输入镜头景别' },
    { label: '反向提示', icon: '🚫', key: 'negative_prompt', placeholder: '请输入反向提示词, 使用--no开头' }
]

// ==================== 接口定义 ====================

/** 基本信息配置（全局） */
export interface AiImagineNamingConfig {
    projectId: number | null
    projectName: string
    jobName: string
    taskDate: Date | null
    prCode: string
    source: string
    extra: string
}

/** 全局生成配置（系统提示词 + 生成类型 + 统一参数） */
export interface AiImagineGlobalConfig {
    systemPrompt: string            // 系统提示词（全部任务生效）
    generateType: AiImagineGenerateType  // 生成类型（全局）
    aspectRatio: string             // 9:16, 16:9, 1:1
    resolution: string              // 480p, 720p
    duration: number                // 6-30s（仅视频有效）
    generateCount: number           // 生成数量 1-6
    provider: string              // 模型提供商（空则使用默认）
}

/** 单个任务数据结构 */
export interface AiImagineTask {
    id: string                      // 前端临时 ID
    userPrompt: string              // 主提示词（画面/动作描述）
    contentSettings: ContentSetting[] // 内容设定（角色形象、画面风格等）
    images: string[]                // JSON 字符串数组 [{id, file_path}]
    storyId?: number                // 关联的故事 ID
    storyTitle?: string             // 关联的故事标题
}

// ==================== 默认值工厂 ====================

export function createDefaultGlobalConfig(): AiImagineGlobalConfig {
    return {
        systemPrompt: '',
        generateType: 'IMAGE_GEN',
        aspectRatio: '1:1',
        resolution: '720p',
        duration: 6,
        generateCount: 2,
        provider: '',
    }
}

export function createDefaultTask(id: string): AiImagineTask {
    return {
        id,
        userPrompt: '',
        contentSettings: [],
        images: [],
    }
}

// ==================== Provide/Inject Keys ====================

/** 模式注入 Key */
export const AIIC_MODE_KEY: InjectionKey<{
    mode: Ref<AiImagineMode>
}> = Symbol('aiicMode')

/** 命名配置注入 Key */
export const AIIC_NAMING_KEY: InjectionKey<{
    baseConfig: Ref<AiImagineNamingConfig>
}> = Symbol('aiicNaming')

/** 全局生成配置注入 Key */
export const AIIC_GLOBAL_CONFIG_KEY: InjectionKey<{
    globalConfig: Ref<AiImagineGlobalConfig>
}> = Symbol('aiicGlobalConfig')

/** 任务列表注入 Key */
export const AIIC_TASK_LIST_KEY: InjectionKey<{
    tasks: Ref<AiImagineTask[]>
    addTask: () => void
    removeTask: (id: string) => void
    copyTask: (id: string) => void
    updateTask: (id: string, partial: Partial<AiImagineTask>) => void
    resetTasks: () => void
}> = Symbol('aiicTaskList')

/** 主逻辑注入 Key */
export const AIIC_MAIN_KEY: InjectionKey<{
    validateConfig: () => boolean
    handleResetAll: () => void
    handleSubmit: () => Promise<void>
    buildSingleTaskPayload: (bc: any, gc: AiImagineGlobalConfig, currentMode: AiImagineMode, task: AiImagineTask, taskIndex?: number) => any
    isSubmitting: Ref<boolean>
}> = Symbol('aiicMain')
