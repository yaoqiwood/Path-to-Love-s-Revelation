/**
 * 环境配置
 * 根据运行环境返回不同的配置
 */

// 环境类型
export type EnvType = 'development' | 'production' | 'test'

// 配置接口
export interface AppConfig {
    // 环境
    env: EnvType
    // API 基础地址
    apiBaseURL: string
    // API 超时时间（毫秒）
    apiTimeout: number
    // 上传文件大小限制（MB）
    maxUploadSize: number
    // 是否启用 Mock 数据
    enableMock: boolean
    // 应用标题
    appTitle: string
    // 是否显示调试信息
    showDebugInfo: boolean
}

// 开发环境配置
const devConfig: AppConfig = {
    env: 'development',
    apiBaseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8011/api',
    apiTimeout: 30000,
    maxUploadSize: 100, // 100MB
    enableMock: false,
    appTitle: 'In Grace - Dev',
    showDebugInfo: true
}

// 生产环境配置
const prodConfig: AppConfig = {
    env: 'production',
    apiBaseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    apiTimeout: 30000,
    maxUploadSize: 100, // 100MB
    enableMock: false,
    appTitle: 'In Grace',
    showDebugInfo: false
}

// 测试环境配置
const testConfig: AppConfig = {
    env: 'test',
    apiBaseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8011/api',
    apiTimeout: 30000,
    maxUploadSize: 50, // 50MB
    enableMock: true,
    appTitle: 'In Grace - Test',
    showDebugInfo: true
}

// 根据环境变量获取配置
function getConfig(): AppConfig {
    const env = (import.meta.env.MODE || 'development') as EnvType

    switch (env) {
        case 'production':
            return prodConfig
        case 'test':
            return testConfig
        case 'development':
        default:
            return devConfig
    }
}

// 导出当前环境的配置
export const config = getConfig()

// 导出配置的简写访问
export const {
    env,
    apiBaseURL,
    apiTimeout,
    maxUploadSize,
    enableMock,
    appTitle,
    showDebugInfo
} = config

// 默认导出
export default config
