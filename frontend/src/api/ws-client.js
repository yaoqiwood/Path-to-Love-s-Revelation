/**
 * WebSocket 客户端封装
 *
 * 提供自动重连、心跳、按类型分发消息的功能。
 * WS 不可用时自动降级（由调用方保持轮询）。
 */
import { wsUrls } from './urls'

const HEARTBEAT_INTERVAL_MS = 30_000
const RECONNECT_DELAYS = [1000, 2000, 4000, 8000, 16000, 30000]

class WsChatClient {
	constructor() {
		/** @type {WebSocket|null} */
		this._ws = null
		this._token = ''
		this._listeners = {}
		this._heartbeatTimer = null
		this._reconnectTimer = null
		this._reconnectAttempt = 0
		this._intentionalClose = false
		this._personnelId = ''
	}

	/**
	 * 连接 WebSocket
	 * @param {string} token - JWT token (不含 "Bearer " 前缀)
	 */
	connect(token) {
		if (!token) return
		this._token = token
		this._intentionalClose = false
		this._doConnect()
	}

	/** 主动断开 */
	disconnect() {
		this._intentionalClose = true
		this._clearReconnect()
		this._clearHeartbeat()
		if (this._ws) {
			try {
				this._ws.close(1000, 'client disconnect')
			} catch (_) {
				/* ignore */
			}
			this._ws = null
		}
	}

	/** 是否处于连接状态 */
	isConnected() {
		return !!(this._ws && this._ws.readyState === WebSocket.OPEN)
	}

	/** 当前 personnel_id (连接成功后服务端返回) */
	get personnelId() {
		return this._personnelId
	}

	/**
	 * 注册消息监听
	 * @param {string} type 消息类型 (new_message / contacts_update / inbox_update / connected)
	 * @param {Function} callback
	 */
	on(type, callback) {
		if (!this._listeners[type]) {
			this._listeners[type] = []
		}
		this._listeners[type].push(callback)
	}

	/** 移除监听 */
	off(type, callback) {
		const list = this._listeners[type]
		if (!list) return
		const idx = list.indexOf(callback)
		if (idx !== -1) list.splice(idx, 1)
	}

	// --- 内部方法 ---

	_doConnect() {
		this._clearReconnect()
		if (this._ws) {
			try {
				this._ws.close()
			} catch (_) {
				/* ignore */
			}
		}
		const url = wsUrls.chat(this._token)
		try {
			this._ws = new WebSocket(url)
		} catch (err) {
			console.warn('[ws-client] WebSocket constructor failed:', err)
			this._scheduleReconnect()
			return
		}

		this._ws.onopen = () => {
			console.log('[ws-client] connected')
			this._reconnectAttempt = 0
			this._startHeartbeat()
		}

		this._ws.onmessage = (event) => {
			let data
			try {
				data = JSON.parse(event.data)
			} catch (_) {
				return
			}
			const type = (data && data.type) || ''

			// 记录 personnel_id
			if (type === 'connected' && data.personnel_id) {
				this._personnelId = data.personnel_id
			}

			// ping from server → reply pong
			if (type === 'ping') {
				this._sendJson({ type: 'pong' })
				return
			}

			// dispatch to listeners
			const callbacks = this._listeners[type]
			if (callbacks && callbacks.length) {
				callbacks.forEach((fn) => {
					try {
						fn(data)
					} catch (err) {
						console.error('[ws-client] listener error:', err)
					}
				})
			}
		}

		this._ws.onclose = (event) => {
			console.log('[ws-client] closed, code:', event.code)
			this._clearHeartbeat()
			this._ws = null
			if (!this._intentionalClose) {
				this._scheduleReconnect()
			}
		}

		this._ws.onerror = (err) => {
			console.warn('[ws-client] error:', err)
		}
	}

	_sendJson(data) {
		if (this._ws && this._ws.readyState === WebSocket.OPEN) {
			this._ws.send(JSON.stringify(data))
		}
	}

	_startHeartbeat() {
		this._clearHeartbeat()
		this._heartbeatTimer = setInterval(() => {
			this._sendJson({ type: 'ping' })
		}, HEARTBEAT_INTERVAL_MS)
	}

	_clearHeartbeat() {
		if (this._heartbeatTimer) {
			clearInterval(this._heartbeatTimer)
			this._heartbeatTimer = null
		}
	}

	_scheduleReconnect() {
		this._clearReconnect()
		const delay = RECONNECT_DELAYS[Math.min(this._reconnectAttempt, RECONNECT_DELAYS.length - 1)]
		console.log(`[ws-client] reconnecting in ${delay}ms (attempt ${this._reconnectAttempt + 1})`)
		this._reconnectTimer = setTimeout(() => {
			this._reconnectAttempt++
			this._doConnect()
		}, delay)
	}

	_clearReconnect() {
		if (this._reconnectTimer) {
			clearTimeout(this._reconnectTimer)
			this._reconnectTimer = null
		}
	}
}

/** 全局单例 */
export const wsChatClient = new WsChatClient()
