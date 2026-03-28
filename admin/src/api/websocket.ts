// WebSocket连接管理

import { io, Socket } from 'socket.io-client'
import { ref } from 'vue'

class WebSocketManager {
    private socket: Socket | null = null
    private url: string
    public connected = ref(false)

    constructor() {
        this.url = import.meta.env.VITE_WS_URL || 'http://localhost:8000'
    }

    // 连接WebSocket
    connect(token?: string) {
        if (this.socket?.connected) return

        this.socket = io(this.url, {
            auth: token ? { token } : undefined,
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000
        })

        this.socket.on('connect', () => {
            console.log('WebSocket connected')
            this.connected.value = true
        })

        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected')
            this.connected.value = false
        })

        this.socket.on('connect_error', (error) => {
            console.error('WebSocket connection error:', error)
        })
    }

    // 断开连接
    disconnect() {
        if (this.socket) {
            this.socket.disconnect()
            this.socket = null
            this.connected.value = false
        }
    }

    // 监听事件
    on(event: string, callback: (...args: any[]) => void) {
        this.socket?.on(event, callback)
    }

    // 移除监听
    off(event: string, callback?: (...args: any[]) => void) {
        if (callback) {
            this.socket?.off(event, callback)
        } else {
            this.socket?.off(event)
        }
    }

    // 发送事件
    emit(event: string, ...args: any[]) {
        this.socket?.emit(event, ...args)
    }

    // 监听任务进度
    onTaskProgress(callback: (data: {
        task_id: string
        status: string
        progress: number
        message?: string
    }) => void) {
        this.on('task_progress', callback)
    }

    // 监听任务完成
    onTaskComplete(callback: (data: {
        task_id: string
        status: string
        result?: any
        error?: string
    }) => void) {
        this.on('task_complete', callback)
    }

    // 监听素材处理完成
    onMaterialReady(callback: (data: {
        material_id: number
        status: string
    }) => void) {
        this.on('material_ready', callback)
    }
}

// 单例导出
export const wsManager = new WebSocketManager()
export default wsManager
