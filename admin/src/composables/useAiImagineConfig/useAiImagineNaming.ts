import { useStorage } from '@vueuse/core'
import { useUserStore } from '@/store/user'
import type { AiImagineNamingConfig } from './types'

function createDefaultNamingConfig(): AiImagineNamingConfig {
    const userStore = useUserStore()
    const currentUserName = userStore.user?.username || ''
    return {
        projectId: null,
        projectName: '',
        jobName: '',
        taskDate: new Date(),
        prCode: currentUserName,
        source: '',
        extra: '',
    }
}


export function useAiImagineNaming() {
    const baseConfig = useStorage<AiImagineNamingConfig>('ct_aiic_naming', createDefaultNamingConfig(), undefined, {
        serializer: {
            read: (v: any) => {
                const parsed = JSON.parse(v)
                // taskDate 不使用缓存，始终使用当天日期
                parsed.taskDate = new Date()
                return parsed
            },
            write: (v: any) => JSON.stringify(v),
        },
    })

    function resetNaming() {
        baseConfig.value = createDefaultNamingConfig()
    }

    return {
        baseConfig,
        resetNaming,
    }
}
