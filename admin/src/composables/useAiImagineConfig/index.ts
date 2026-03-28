import { ref, provide, watch, inject } from 'vue'
import { useStorage } from '@vueuse/core'
import { ElMessage } from 'element-plus'

import { useAiImagineNaming } from './useAiImagineNaming'
import { useAiImagineTaskList } from './useAiImagineTaskList'
import { aiImagineJobApi } from '@/api/aiImagineJob'
import type { AiImagineJobBatchCreate } from '@/api/aiImagineJob'

import {
    AIIC_MODE_KEY,
    AIIC_NAMING_KEY,
    AIIC_GLOBAL_CONFIG_KEY,
    AIIC_TASK_LIST_KEY,
    AIIC_MAIN_KEY,
    createDefaultGlobalConfig,
} from './types'
import type { AiImagineMode, AiImagineTask, AiImagineGlobalConfig } from './types'

/**
 * Provider Hook: 初始化状态并提供给子组件
 * 应该仅在 Provider 组件或根级容器组件中调用一次
 */
export function useAiImagineConfigProvider() {
    // ==================== 初始化子 hooks ====================
    const naming = useAiImagineNaming()
    const taskList = useAiImagineTaskList()

    // ==================== 模式状态 ====================
    const mode = useStorage<AiImagineMode>('ct_aiic_mode', 'image')

    // ==================== 全局生成配置 ====================
    const globalConfig = useStorage<AiImagineGlobalConfig>('ct_aiic_global_config', createDefaultGlobalConfig())

    // 切换生成类型时，自动清空任务列表
    watch(() => globalConfig.value.generateType, () => {
        taskList.resetTasks()
    })

    // ==================== 校验 ====================
    function validateConfig(): boolean {
        const bc = naming.baseConfig.value

        if (!bc.projectId) {
            ElMessage.warning('请先选择关联项目')
            return false
        }

        if (taskList.tasks.value.length === 0) {
            ElMessage.warning('请至少添加一个任务')
            return false
        }

        for (let i = 0; i < taskList.tasks.value.length; i++) {
            const task = taskList.tasks.value[i]
            if (!task) continue

            const idx = i + 1

            // text 模式不需要图片，image / multi_image 需要
            if (mode.value !== 'text' && task.images.length === 0) {
                ElMessage.warning(`任务 ${idx}: 请上传参考图片`)
                return false
            }

            // 至少需要全局系统提示词或单任务用户提示词其中之一
            const hasSystem = globalConfig.value.systemPrompt.trim().length > 0
            const hasUser = task.userPrompt.trim().length > 0
            if (!hasSystem && !hasUser) {
                ElMessage.warning(`任务 ${idx}: 请填写系统提示词或用户提示词`)
                return false
            }
        }

        return true
    }

    // ==================== 提取单个任务构造逻辑 ====================
    function buildSingleTaskPayload(
        bc: any,
        gc: AiImagineGlobalConfig,
        currentMode: AiImagineMode,
        task: AiImagineTask,
        taskIndex: number = 0
    ): AiImagineJobBatchCreate {
        const currentImagePaths: string[] = []

        if (currentMode === 'image' || gc.generateType === 'IMAGE_RECOGNITION') {
            // 单图模式或图片理解：取第一张
            const ref = task.images[0]
            if (ref) {
                try {
                    const parsed = JSON.parse(ref).file_path
                    currentImagePaths.push(parsed || '')
                } catch {
                    currentImagePaths.push('')
                }
            } else {
                currentImagePaths.push('')
            }
        } else if (currentMode === 'multi_image') {
            // 多图融合模式：收集所有图
            const paths = task.images.map((json: string) => {
                try { return JSON.parse(json).file_path || '' } catch { return '' }
            }).filter(Boolean)
            currentImagePaths.push(...paths)
        }

        // 拼接主提示词 + 内容设定
        let fullPrompt = gc.generateType === 'IMAGE_GEN' || gc.generateType === 'VIDEO_GEN' ? ("[brief]: " + task.userPrompt) : task.userPrompt
        if ((task.contentSettings ?? []).length > 0) {
            const settingsText = (task.contentSettings ?? [])
                .filter(s => s.content.trim())
                .map(s => `[${s.key}]: ${s.content}`)
                .join('\n')
            if (settingsText) {
                fullPrompt = fullPrompt ? `${fullPrompt}\n${settingsText}` : settingsText
            }
        }

        let signValue = `任务 ${(taskIndex + 1)}`
        if (gc.generateType === 'TEXT_ANALYSIS' && task.storyTitle) {
            signValue = task.storyTitle
        }

        const input = {
            prompt: fullPrompt,
            image_paths: currentImagePaths,
            sign: signValue
        }

        // 构建参数对象
        let jobParam: any = {}
        if (gc.generateType === 'IMAGE_RECOGNITION' || gc.generateType === 'TEXT_ANALYSIS') {
            jobParam = { mode: 'text' }
        } else if (gc.generateType === 'VIDEO_GEN') {
            jobParam = {
                mode: currentMode,
                duration: gc.duration,
                aspect_ratio: gc.aspectRatio,
                resolution: gc.resolution,
                n: gc.generateCount,
            }
        } else {
            jobParam = {
                mode: currentMode,
                aspect_ratio: gc.aspectRatio,
                n: gc.generateCount,
                ...(gc.provider ? { provider: gc.provider } : {}),
            }
        }

        return {
            project_id: bc.projectId,
            job_name: bc.jobName,
            job_type: gc.generateType,
            system_prompt: gc.systemPrompt,
            inputs: [input],
            param: jobParam,
        }
    }

    // ==================== 提交 ====================
    const isSubmitting = ref(false)

    async function handleSubmit() {
        if (!validateConfig()) return

        isSubmitting.value = true
        try {
            const bc = naming.baseConfig.value
            const gc = globalConfig.value
            const tasks = taskList.tasks.value

            // 将所有任务打包为一个 Job 的 N 个 input
            const inputs: { prompt: string; image_paths: string[] }[] = []

            // 构建参数对象从第一个 task 获取
            const defaultTask: AiImagineTask = { id: '', userPrompt: '', images: [], contentSettings: [] }
            const samplePayload = buildSingleTaskPayload(bc, gc, mode.value, tasks[0] || defaultTask, 0)
            const jobParam = samplePayload.param

            tasks.forEach((task: AiImagineTask, index: number) => {
                const singlePayload = buildSingleTaskPayload(bc, gc, mode.value, task, index)
                inputs.push(singlePayload.inputs[0]!)
            })

            const payload: AiImagineJobBatchCreate = {
                project_id: bc.projectId,
                job_name: bc.jobName,
                job_type: gc.generateType,
                system_prompt: gc.systemPrompt,
                inputs,
                param: jobParam,
            }

            const result = await aiImagineJobApi.batchCreate(payload)
            ElMessage.success(`已成功创建任务，包含 ${result.input_count} 个输入组`)
        } catch (error: any) {
            console.error(error)
            ElMessage.error(error?.response?.data?.detail || '任务创建失败')
        } finally {
            isSubmitting.value = false
        }
    }

    // ==================== 重置 ====================
    function handleResetAll() {
        naming.resetNaming()
        taskList.resetTasks()
        globalConfig.value = createDefaultGlobalConfig()
        mode.value = 'image'
    }

    // ==================== Provide 注入 ====================

    provide(AIIC_MODE_KEY, { mode })
    provide(AIIC_NAMING_KEY, { baseConfig: naming.baseConfig })
    provide(AIIC_GLOBAL_CONFIG_KEY, { globalConfig })
    provide(AIIC_TASK_LIST_KEY, {
        tasks: taskList.tasks,
        addTask: taskList.addTask,
        removeTask: taskList.removeTask,
        copyTask: taskList.copyTask,
        updateTask: taskList.updateTask,
        resetTasks: taskList.resetTasks,
    })
    provide(AIIC_MAIN_KEY, {
        validateConfig,
        handleResetAll,
        handleSubmit,
        buildSingleTaskPayload,
        isSubmitting,
    })

    return {
        naming,
        taskList,
        mode,
        globalConfig,
        handleResetAll,
        validateConfig,
        handleSubmit,
        buildSingleTaskPayload,
        isSubmitting,
    }
}

/**
 * Consumer Hook: 获取注入的状态
 * 必须在 AiImagineConfigProvider 的子组件中调用
 */
export function useAiImagineConfig() {
    const modeCtx = inject(AIIC_MODE_KEY)
    const namingCtx = inject(AIIC_NAMING_KEY)
    const globalConfigCtx = inject(AIIC_GLOBAL_CONFIG_KEY)
    const taskListCtx = inject(AIIC_TASK_LIST_KEY)
    const mainCtx = inject(AIIC_MAIN_KEY)

    if (!modeCtx || !namingCtx || !globalConfigCtx || !taskListCtx || !mainCtx) {
        throw new Error('useAiImagineConfig must be used within AiImagineConfigProvider')
    }

    return {
        mode: modeCtx.mode,
        baseConfig: namingCtx.baseConfig,
        globalConfig: globalConfigCtx.globalConfig,
        taskList: taskListCtx,
        ...mainCtx,
    }
}
