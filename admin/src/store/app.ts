// 应用全局状态管理

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
    // 状态
    const languages = ref<Record<string, string>>({})
    const languageOptions = ref<{ label: string; value: string }[]>([])

    // 初始化配置
    async function initConfigs() {
        // Fallback defaults
        languageOptions.value = [
            { label: '简体中文', value: 'zh-CN' },
            { label: '繁体中文', value: 'zh-TW' },
            { label: '英文', value: 'en' },
            { label: '日文', value: 'ja' },
            { label: '韩文', value: 'ko' },
            { label: '泰文', value: 'th' },
            { label: '越南文', value: 'vi' },
            { label: '阿拉伯文', value: 'ar' }
        ]
    }

    return {
        languages,
        languageOptions,
        initConfigs
    }
})
