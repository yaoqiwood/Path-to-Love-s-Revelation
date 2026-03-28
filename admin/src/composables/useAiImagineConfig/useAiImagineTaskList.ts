
import { useStorage } from '@vueuse/core'
import { createDefaultTask } from './types'
import type { AiImagineTask } from './types'

const genId = () => {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID().slice(0, 8)
    }
    return Math.random().toString(36).substring(2, 10)
}

export function useAiImagineTaskList() {
    const tasks = useStorage<AiImagineTask[]>('ct_aiic_tasks', [])

    function addTask() {
        if (tasks.value.length >= 10) return  // 最多 10 个任务
        tasks.value.push(createDefaultTask(genId()))
    }

    function removeTask(id: string) {
        tasks.value = tasks.value.filter(t => t.id !== id)
    }

    function copyTask(id: string) {
        if (tasks.value.length >= 10) return  // 最多 10 个任务
        const source = tasks.value.find(t => t.id === id)
        if (!source) return
        const copied: AiImagineTask = {
            ...JSON.parse(JSON.stringify(source)),
            id: genId(),
        }
        const idx = tasks.value.findIndex(t => t.id === id)
        tasks.value.splice(idx + 1, 0, copied)
    }

    function updateTask(id: string, partial: Partial<AiImagineTask>) {
        const task = tasks.value.find(t => t.id === id)
        if (task) {
            Object.assign(task, partial)
        }
    }

    function resetTasks() {
        tasks.value = []
    }

    return {
        tasks,
        addTask,
        removeTask,
        copyTask,
        updateTask,
        resetTasks,
    }
}
