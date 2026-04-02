<template>
	<section class="page-shell">
		<div class="page-backdrop page-backdrop-left"></div>
		<div class="page-backdrop page-backdrop-right"></div>

		<section v-if="!isAuthorized" class="auth-panel">
			<div class="panel-head">
				<p class="eyebrow">PRIVATE API TOOL</p>
				<h1 class="panel-title">管理员验证</h1>
				<p class="panel-copy">
					此页面不会出现在主页或后台导航中，只有直接访问
					<code>/api_tester</code>
					才能进入。验证通过后才会显示接口调用工具。
				</p>
			</div>

			<div class="field-block">
				<label class="field-label" for="tester-username">管理员账号</label>
				<input
					id="tester-username"
					v-model.trim="loginForm.username"
					class="text-input"
					type="text"
					autocomplete="off"
					placeholder="请输入管理员账号"
					:disabled="isAuthorizing"
					@keyup.enter="handleAdminLogin"
				/>
			</div>

			<div class="field-block">
				<label class="field-label" for="tester-password">管理员密码</label>
				<input
					id="tester-password"
					v-model="loginForm.password"
					class="text-input"
					type="password"
					autocomplete="off"
					placeholder="请输入管理员密码"
					:disabled="isAuthorizing"
					@keyup.enter="handleAdminLogin"
				/>
			</div>

			<p class="status-text" :class="authStatusClass">{{ authStatusText }}</p>

			<div class="action-row">
				<button class="primary-btn" type="button" :disabled="isAuthSubmitDisabled" @click="handleAdminLogin">
					{{ isAuthorizing ? '验证中...' : '进入 API 工具' }}
				</button>
			</div>
		</section>

		<section v-else class="tool-shell">
			<header class="hero-card">
				<div class="panel-head">
					<p class="eyebrow">PRIVATE API TOOL</p>
					<h1 class="panel-title">API 调用工具</h1>
					<p class="panel-copy">
						接口列表直接读取
						<code>src/api/urls.js</code>
						，支持 GET / POST、参数保存，以及可选把本次返回结果一起保存。
					</p>
				</div>

				<div class="hero-meta">
					<p class="meta-item">当前账号：{{ authSession.username || 'admin' }}</p>
					<p class="meta-item token-item">Token：{{ maskedToken }}</p>
				</div>

				<div class="hero-actions">
					<button class="ghost-btn" type="button" @click="handleResetForm">新建请求</button>
					<button class="ghost-btn" type="button" @click="handleLogout">退出工具</button>
				</div>
			</header>

			<div class="workspace-grid">
				<section class="panel-card editor-card">
					<div class="panel-head">
						<h2 class="section-title">请求编辑</h2>
						<p class="section-copy">动态路由会以 <code>:id</code> 形式展示，执行前请在路径输入框中替换成真实值。</p>
					</div>

					<div class="field-grid">
						<div class="field-block">
							<label class="field-label" for="preset-name">保存名称</label>
							<input
								id="preset-name"
								v-model.trim="formState.presetName"
								class="text-input"
								type="text"
								placeholder="例如：人员登录调试"
							/>
						</div>

						<div class="field-block">
							<label class="field-label" for="request-method">请求方法</label>
							<select id="request-method" v-model="formState.method" class="select-input">
								<option value="GET">GET</option>
								<option value="POST">POST</option>
							</select>
						</div>
					</div>

					<div class="field-block">
						<label class="field-label" for="endpoint-select">接口选择</label>
						<select
							id="endpoint-select"
							v-model="formState.endpointKey"
							class="select-input"
							@change="handleEndpointChange"
						>
							<option v-for="item in endpointOptions" :key="item.key" :value="item.key">
								{{ item.label }}
							</option>
						</select>
						<p class="field-tip">
							当前模板：<code>{{ selectedEndpointTemplate }}</code>
						</p>
					</div>

					<div class="field-block">
						<label class="field-label" for="request-path">请求路径</label>
						<input
							id="request-path"
							v-model.trim="formState.requestPath"
							class="text-input"
							type="text"
							placeholder="/api/personnel/login-profile"
						/>
					</div>

					<div class="field-block">
						<label class="field-label" for="request-params">
							{{ formState.method === 'GET' ? '查询参数 JSON' : '请求体 JSON' }}
						</label>
						<textarea
							id="request-params"
							v-model="formState.paramsText"
							class="json-editor"
							spellcheck="false"
							placeholder="{&#10;  &quot;username&quot;: &quot;admin&quot;,&#10;  &quot;password&quot;: &quot;123456&quot;&#10;}"
						></textarea>
					</div>

					<label class="checkbox-row">
						<input v-model="formState.includeResponseWhenSaving" type="checkbox" />
						<span>保存时附带当前返回结果</span>
					</label>

					<p class="status-text" :class="requestStatusClass">{{ requestStatusText }}</p>

					<div class="action-row">
						<button class="primary-btn" type="button" :disabled="isExecuting" @click="handleExecuteRequest">
							{{ isExecuting ? '请求发送中...' : '发送请求' }}
						</button>
						<button class="ghost-btn" type="button" @click="handleSavePreset">保存配置</button>
					</div>
				</section>

				<section class="panel-card saved-card">
					<div class="panel-head">
						<h2 class="section-title">已保存请求</h2>
						<p class="section-copy">保存内容包含方法、接口路径、参数；勾选后会一起保存最近一次响应。</p>
					</div>

					<div v-if="!savedPresets.length" class="empty-box">
						<p>当前还没有保存的请求。</p>
					</div>

					<div v-else class="saved-list">
						<article
							v-for="item in savedPresets"
							:key="item.id"
							class="saved-item"
							:class="activePresetId === item.id ? 'is-active' : ''"
						>
							<div class="saved-top">
								<div>
									<h3 class="saved-title">{{ item.name }}</h3>
									<p class="saved-meta">{{ item.method }} · {{ item.requestPath }}</p>
								</div>
								<p class="saved-time">{{ formatDateTime(item.updatedAt) }}</p>
							</div>

							<div class="saved-actions">
								<button class="mini-btn" type="button" @click="handleLoadPreset(item.id)">载入</button>
								<button class="mini-btn danger-btn" type="button" @click="handleDeletePreset(item.id)">
									删除
								</button>
							</div>
						</article>
					</div>
				</section>
			</div>

			<section class="panel-card response-card">
				<div class="response-head">
					<div class="panel-head">
						<h2 class="section-title">返回结果</h2>
						<p class="section-copy">最近一次请求的状态码、耗时和响应内容会展示在这里。</p>
					</div>
					<div class="response-stats">
						<p class="meta-item">状态码：{{ responseState.statusCode || '-' }}</p>
						<p class="meta-item">耗时：{{ responseState.durationLabel }}</p>
					</div>
				</div>

				<textarea
					:value="responseState.responseText"
					class="response-viewer"
					readonly
					spellcheck="false"
				></textarea>
			</section>
		</section>
	</section>
</template>

<script setup>
	import { computed, reactive, ref } from 'vue'

	import { apiUrls } from '@/api/urls'
	import { http, unwrapResponse } from '@/api/http'
	import { app } from '@/platform/app-bridge'

	const ADMIN_AUTH_STORAGE_KEY = 'private-api-tester-admin-auth'
	const SAVED_PRESET_STORAGE_KEY = 'private-api-tester-saved-presets'
	const DEFAULT_LOGIN_ENDPOINT_KEY = 'users.login'
	const DEFAULT_LOGIN_REQUEST = '{\n  "username": "admin",\n  "password": "123456"\n}'

	function parseFunctionParamNames(handler) {
		const source = String(handler || '')
		const match =
			source.match(/^[^(]*\(\s*([^)]*)\)/) ||
			source.match(/^\s*([^=()]+?)\s*=>/)

		if (!match || !match[1]) {
			return []
		}

		return match[1]
			.split(',')
			.map((item) => item.trim().replace(/=.*$/, '').trim())
			.filter(Boolean)
	}

	function buildEndpointPath(handler) {
		if (typeof handler !== 'function') {
			return ''
		}

		const paramNames = parseFunctionParamNames(handler)
		const placeholderArgs = Array.from({ length: handler.length }, (_, index) => {
			const paramName = paramNames[index] || `param${index + 1}`
			return `:${paramName}`
		})

		return handler(...placeholderArgs)
	}

	function collectEndpointOptions(node, parents = []) {
		return Object.keys(node || {}).flatMap((key) => {
			const value = node[key]
			const nextParents = [...parents, key]

			if (typeof value === 'function') {
				const endpointKey = nextParents.join('.')
				const endpointPath = buildEndpointPath(value)
				return [
					{
						key: endpointKey,
						label: `${endpointKey}  ${endpointPath}`,
						path: endpointPath
					}
				]
			}

			if (value && typeof value === 'object') {
				return collectEndpointOptions(value, nextParents)
			}

			return []
		})
	}

	function loadStoredValue(key, fallbackValue) {
		try {
			const storedValue = app.getStorageSync(key)
			return storedValue == null || storedValue === '' ? fallbackValue : storedValue
		} catch (error) {
			return fallbackValue
		}
	}

	function persistStoredValue(key, value) {
		app.setStorageSync(key, value)
	}

	function removeStoredValue(key) {
		app.removeStorageSync(key)
	}

	function isPlainObject(value) {
		return !!value && Object.prototype.toString.call(value) === '[object Object]'
	}

	function parseEditorJson(rawValue, { allowEmptyObject = true } = {}) {
		const normalizedValue = String(rawValue || '').trim()
		if (!normalizedValue) {
			return allowEmptyObject ? {} : null
		}

		try {
			return JSON.parse(normalizedValue)
		} catch (error) {
			throw new Error('参数不是合法 JSON，请检查后重试。')
		}
	}

	function formatJson(value) {
		try {
			return JSON.stringify(value, null, 2)
		} catch (error) {
			return String(value || '')
		}
	}

	function buildAuthorizationHeader(session) {
		const accessToken = String(session?.accessToken || '').trim()
		if (!accessToken) {
			return ''
		}

		const tokenType = String(session?.tokenType || 'bearer').trim()
		return `${tokenType.toLowerCase() === 'bearer' ? 'Bearer' : tokenType} ${accessToken}`.trim()
	}

	function createDefaultResponseState() {
		return {
			statusCode: '',
			durationLabel: '-',
			responseText: '{\n  "message": "还没有发送请求"\n}'
		}
	}

	function formatDateTime(value) {
		if (!value) {
			return '-'
		}

		const date = new Date(value)
		if (Number.isNaN(date.getTime())) {
			return '-'
		}

		return date.toLocaleString('zh-CN', {
			hour12: false
		})
	}

	const endpointOptions = collectEndpointOptions(apiUrls).sort((left, right) =>
		left.key.localeCompare(right.key, 'zh-Hans-CN')
	)

	const defaultEndpoint =
		endpointOptions.find((item) => item.key === DEFAULT_LOGIN_ENDPOINT_KEY) || endpointOptions[0] || null

	const loginForm = reactive({
		username: 'admin',
		password: '123456'
	})
	const formState = reactive({
		presetName: '',
		method: 'POST',
		endpointKey: defaultEndpoint?.key || '',
		requestPath: defaultEndpoint?.path || '/api/users/login',
		paramsText: DEFAULT_LOGIN_REQUEST,
		includeResponseWhenSaving: false
	})

	const initialAuthSession = loadStoredValue(ADMIN_AUTH_STORAGE_KEY, null)
	const initialSavedPresets = loadStoredValue(SAVED_PRESET_STORAGE_KEY, [])

	const authSession = ref(initialAuthSession && typeof initialAuthSession === 'object' ? initialAuthSession : null)
	const savedPresets = ref(Array.isArray(initialSavedPresets) ? initialSavedPresets : [])
	const activePresetId = ref('')
	const isAuthorizing = ref(false)
	const isExecuting = ref(false)
	const authStatusText = ref('请输入管理员账号和密码进行验证。')
	const requestStatusText = ref('请选择接口、填写参数，然后发送请求。')
	const responseState = ref(createDefaultResponseState())

	const isAuthorized = computed(() => !!String(authSession.value?.accessToken || '').trim())
	const isAuthSubmitDisabled = computed(
		() => isAuthorizing.value || !loginForm.username.trim() || !loginForm.password
	)
	const authStatusClass = computed(() =>
		authStatusText.value.includes('失败') || authStatusText.value.includes('错误') ? 'is-error' : 'is-neutral'
	)
	const requestStatusClass = computed(() =>
		requestStatusText.value.includes('失败') || requestStatusText.value.includes('错误')
			? 'is-error'
			: requestStatusText.value.includes('成功')
				? 'is-success'
				: 'is-neutral'
	)
	const selectedEndpointTemplate = computed(() => {
		const matchedItem = endpointOptions.find((item) => item.key === formState.endpointKey)
		return matchedItem?.path || formState.requestPath || '-'
	})
	const maskedToken = computed(() => {
		const accessToken = String(authSession.value?.accessToken || '').trim()
		if (!accessToken) {
			return '-'
		}

		if (accessToken.length <= 16) {
			return accessToken
		}

		return `${accessToken.slice(0, 12)}...${accessToken.slice(-8)}`
	})

	function syncSavedPresets() {
		persistStoredValue(SAVED_PRESET_STORAGE_KEY, savedPresets.value)
	}

	function handleEndpointChange() {
		const matchedItem = endpointOptions.find((item) => item.key === formState.endpointKey)
		if (!matchedItem) {
			return
		}

		formState.requestPath = matchedItem.path
		if (matchedItem.key === DEFAULT_LOGIN_ENDPOINT_KEY && !formState.paramsText.trim()) {
			formState.method = 'POST'
			formState.paramsText = DEFAULT_LOGIN_REQUEST
		}
	}

	async function handleAdminLogin() {
		if (isAuthSubmitDisabled.value) {
			return
		}

		isAuthorizing.value = true
		authStatusText.value = '正在验证管理员身份...'

		try {
			const response = await http.post(
				apiUrls.users.login(),
				{
					username: loginForm.username.trim(),
					password: loginForm.password
				},
				{
					skipAuthRedirect: true,
					skipUserSessionAuth: true
				}
			)
			const result = unwrapResponse(response)
			const accessToken = String(result?.access_token || '').trim()
			if (!accessToken) {
				throw new Error('管理员登录成功，但未返回 access_token。')
			}

			authSession.value = {
				username: loginForm.username.trim(),
				accessToken,
				tokenType: result?.token_type || 'bearer',
				loggedAt: Date.now()
			}
			persistStoredValue(ADMIN_AUTH_STORAGE_KEY, authSession.value)
			authStatusText.value = '管理员验证成功。'
			requestStatusText.value = '管理员验证成功，现在可以直接发送接口请求。'
			loginForm.password = ''
			app.showToast({
				title: '验证成功',
				icon: 'none'
			})
		} catch (error) {
			authSession.value = null
			removeStoredValue(ADMIN_AUTH_STORAGE_KEY)
			authStatusText.value = error?.message || '管理员验证失败。'
		} finally {
			isAuthorizing.value = false
		}
	}

	function handleLogout() {
		authSession.value = null
		removeStoredValue(ADMIN_AUTH_STORAGE_KEY)
		authStatusText.value = '已退出管理员验证，请重新输入账号密码。'
		requestStatusText.value = '管理员验证已失效，请重新登录后再调用接口。'
	}

	function handleResetForm() {
		activePresetId.value = ''
		formState.presetName = ''
		formState.method = 'POST'
		formState.endpointKey = defaultEndpoint?.key || ''
		formState.requestPath = defaultEndpoint?.path || '/api/users/login'
		formState.paramsText = DEFAULT_LOGIN_REQUEST
		formState.includeResponseWhenSaving = false
		requestStatusText.value = '已重置当前请求表单。'
		responseState.value = createDefaultResponseState()
	}

	function buildRequestConfig() {
		const authHeader = buildAuthorizationHeader(authSession.value)
		const config = {
			skipAuthRedirect: true,
			skipUserSessionAuth: true,
			headers: {}
		}

		if (authHeader) {
			config.headers.Authorization = authHeader
		}

		return config
	}

	async function handleExecuteRequest() {
		if (!isAuthorized.value) {
			requestStatusText.value = '请先完成管理员验证。'
			return
		}

		const requestPath = String(formState.requestPath || '').trim()
		if (!requestPath) {
			requestStatusText.value = '请求路径不能为空。'
			return
		}

		let parsedPayload = {}
		try {
			parsedPayload = parseEditorJson(formState.paramsText)
		} catch (error) {
			requestStatusText.value = error.message
			return
		}

		if (formState.method === 'GET' && !isPlainObject(parsedPayload)) {
			requestStatusText.value = 'GET 请求参数必须是 JSON 对象。'
			return
		}

		isExecuting.value = true
		requestStatusText.value = '正在发送请求...'
		const startedAt = performance.now()

		try {
			const config = buildRequestConfig()
			let response

			if (formState.method === 'GET') {
				response = await http.get(requestPath, {
					...config,
					params: parsedPayload
				})
			} else {
				response = await http.post(requestPath, parsedPayload, config)
			}

			const duration = Math.max(0, Math.round(performance.now() - startedAt))
			responseState.value = {
				statusCode: response?.status || 200,
				durationLabel: `${duration} ms`,
				responseText: formatJson(unwrapResponse(response))
			}
			requestStatusText.value = '请求发送成功。'
		} catch (error) {
			const duration = Math.max(0, Math.round(performance.now() - startedAt))
			const errorPayload = error?.response?.data || {
				message: error?.message || '请求失败'
			}

			responseState.value = {
				statusCode: error?.response?.status || '',
				durationLabel: `${duration} ms`,
				responseText: formatJson(errorPayload)
			}
			requestStatusText.value = error?.message || '请求失败。'
		} finally {
			isExecuting.value = false
		}
	}

	function handleSavePreset() {
		const requestPath = String(formState.requestPath || '').trim()
		if (!requestPath) {
			requestStatusText.value = '请先填写请求路径，再保存。'
			return
		}

		const presetName =
			String(formState.presetName || '').trim() ||
			`${formState.method} ${requestPath}`

		const presetId = activePresetId.value || `api-preset-${Date.now()}`
		const nextPreset = {
			id: presetId,
			name: presetName,
			method: formState.method,
			endpointKey: formState.endpointKey,
			requestPath,
			paramsText: formState.paramsText,
			includeResponseWhenSaving: !!formState.includeResponseWhenSaving,
			responseText: formState.includeResponseWhenSaving ? responseState.value.responseText : '',
			updatedAt: Date.now()
		}

		const nextList = savedPresets.value.filter((item) => item.id !== presetId)
		nextList.unshift(nextPreset)
		savedPresets.value = nextList
		activePresetId.value = presetId
		formState.presetName = presetName
		syncSavedPresets()
		requestStatusText.value = '当前请求已保存。'
	}

	function handleLoadPreset(presetId) {
		const matchedPreset = savedPresets.value.find((item) => item.id === presetId)
		if (!matchedPreset) {
			return
		}

		activePresetId.value = matchedPreset.id
		formState.presetName = matchedPreset.name || ''
		formState.method = matchedPreset.method || 'GET'
		formState.endpointKey = matchedPreset.endpointKey || ''
		formState.requestPath = matchedPreset.requestPath || ''
		formState.paramsText = matchedPreset.paramsText || '{}'
		formState.includeResponseWhenSaving = !!matchedPreset.includeResponseWhenSaving

		if (matchedPreset.responseText) {
			responseState.value = {
				statusCode: '',
				durationLabel: '已保存',
				responseText: matchedPreset.responseText
			}
		}

		requestStatusText.value = `已载入保存项：${matchedPreset.name}`
	}

	function handleDeletePreset(presetId) {
		savedPresets.value = savedPresets.value.filter((item) => item.id !== presetId)
		syncSavedPresets()

		if (activePresetId.value === presetId) {
			handleResetForm()
		}

		requestStatusText.value = '已删除保存项。'
	}
</script>

<style scoped lang="less">
	.page-shell {
		position: relative;
		min-height: 100vh;
		padding: 32px 20px 40px;
		background:
			radial-gradient(circle at top left, rgba(255, 211, 174, 0.45), transparent 28%),
			radial-gradient(circle at 82% 14%, rgba(120, 182, 255, 0.22), transparent 24%),
			linear-gradient(180deg, #f7f1e8 0%, #fefcf8 50%, #f0ebe3 100%);
		box-sizing: border-box;
	}

	.page-backdrop {
		position: fixed;
		border-radius: 999px;
		filter: blur(24px);
		pointer-events: none;
		opacity: 0.5;
	}

	.page-backdrop-left {
		top: -60px;
		left: -40px;
		width: 220px;
		height: 220px;
		background: rgba(255, 180, 124, 0.45);
	}

	.page-backdrop-right {
		right: -60px;
		bottom: -80px;
		width: 260px;
		height: 260px;
		background: rgba(102, 149, 255, 0.18);
	}

	.auth-panel,
	.hero-card,
	.panel-card {
		position: relative;
		z-index: 1;
		width: min(1120px, 100%);
		margin: 0 auto;
		border: 1px solid rgba(99, 75, 48, 0.12);
		border-radius: 28px;
		background: rgba(255, 252, 247, 0.9);
		box-shadow: 0 22px 52px rgba(71, 52, 31, 0.1);
		backdrop-filter: blur(14px);
	}

	.auth-panel {
		max-width: 520px;
		padding: 32px 28px;
		margin-top: 6vh;
	}

	.tool-shell {
		position: relative;
		z-index: 1;
		width: min(1240px, 100%);
		margin: 0 auto;
	}

	.hero-card {
		display: grid;
		grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.9fr) auto;
		gap: 24px;
		align-items: start;
		padding: 30px 30px 24px;
	}

	.panel-card {
		padding: 24px;
	}

	.workspace-grid {
		display: grid;
		grid-template-columns: minmax(0, 1.65fr) minmax(360px, 0.95fr);
		gap: 24px;
		margin-top: 20px;
		align-items: start;
	}

	.response-card {
		margin-top: 20px;
	}

	.panel-head {
		display: flex;
		flex-direction: column;
		min-width: 0;
	}

	.eyebrow {
		margin: 0;
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.24em;
		color: #9e6c2e;
		text-transform: uppercase;
	}

	.panel-title,
	.section-title,
	.saved-title {
		margin: 0;
		color: #2d241c;
	}

	.panel-title {
		margin-top: 10px;
		font-size: clamp(28px, 4vw, 38px);
		line-height: 1.12;
	}

	.panel-copy,
	.section-copy,
	.field-tip,
	.saved-meta,
	.saved-time,
	.meta-item {
		margin: 0;
		font-size: 14px;
		line-height: 1.7;
		color: #6c5b4e;
	}

	.panel-copy,
	.section-copy {
		margin-top: 12px;
	}

	.hero-meta {
		display: grid;
		gap: 10px;
		align-content: start;
	}

	.token-item {
		word-break: break-all;
		overflow-wrap: anywhere;
	}

	.hero-actions,
	.action-row,
	.saved-actions,
	.response-head,
	.saved-top {
		display: flex;
		align-items: center;
	}

	.hero-actions,
	.action-row,
	.saved-actions {
		gap: 12px;
	}

	.hero-actions {
		margin-top: 0;
		justify-self: end;
		align-self: start;
		flex-wrap: wrap;
		justify-content: flex-end;
	}

	.response-head,
	.saved-top {
		justify-content: space-between;
		gap: 12px;
	}

	.response-head {
		align-items: flex-start;
	}

	.field-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 16px;
	}

	.field-block {
		margin-top: 18px;
	}

	.field-label {
		display: block;
		margin-bottom: 8px;
		font-size: 14px;
		font-weight: 700;
		color: #3c2f25;
	}

	.text-input,
	.select-input,
	.json-editor,
	.response-viewer {
		width: 100%;
		border: 1px solid rgba(123, 96, 67, 0.18);
		border-radius: 18px;
		background: #fffdfa;
		color: #2f251c;
		box-sizing: border-box;
	}

	.text-input,
	.select-input {
		height: 48px;
		padding: 0 14px;
		font-size: 14px;
	}

	.json-editor,
	.response-viewer {
		min-height: 220px;
		padding: 14px 16px;
		font-size: 13px;
		line-height: 1.65;
		font-family:
			'SFMono-Regular',
			'Consolas',
			'Liberation Mono',
			monospace;
		resize: vertical;
	}

	.response-viewer {
		margin-top: 18px;
		min-height: 320px;
		background: #fffefb;
	}

	.field-tip {
		margin-top: 8px;
		overflow-wrap: anywhere;
	}

	.checkbox-row {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		margin-top: 16px;
		font-size: 14px;
		color: #3f3127;
	}

	.status-text {
		margin: 16px 0 0;
		font-size: 14px;
		line-height: 1.6;
	}

	.status-text.is-error {
		color: #bf3d2f;
	}

	.status-text.is-success {
		color: #1f7a47;
	}

	.status-text.is-neutral {
		color: #6c5b4e;
	}

	.primary-btn,
	.ghost-btn,
	.mini-btn {
		border: 0;
		border-radius: 999px;
		cursor: pointer;
		transition:
			transform 0.2s ease,
			box-shadow 0.2s ease,
			opacity 0.2s ease;
	}

	.primary-btn,
	.ghost-btn {
		min-width: 124px;
		height: 46px;
		padding: 0 18px;
		font-size: 14px;
		font-weight: 700;
	}

	.primary-btn {
		background: linear-gradient(135deg, #d17c38, #b45228);
		color: #fffaf7;
		box-shadow: 0 16px 30px rgba(180, 82, 40, 0.24);
	}

	.ghost-btn,
	.mini-btn {
		background: rgba(255, 248, 240, 0.92);
		color: #5c4533;
		border: 1px solid rgba(123, 96, 67, 0.18);
	}

	.mini-btn {
		height: 34px;
		padding: 0 12px;
		font-size: 13px;
	}

	.danger-btn {
		color: #a63d32;
	}

	.primary-btn:hover,
	.ghost-btn:hover,
	.mini-btn:hover {
		transform: translateY(-1px);
	}

	.primary-btn:disabled {
		cursor: not-allowed;
		opacity: 0.6;
		box-shadow: none;
	}

	.saved-list {
		margin-top: 18px;
		display: grid;
		gap: 14px;
		max-height: 620px;
		overflow: auto;
		padding-right: 2px;
	}

	.saved-item,
	.empty-box {
		border-radius: 20px;
		border: 1px solid rgba(123, 96, 67, 0.14);
		background: #fffdfa;
		padding: 16px;
	}

	.saved-item.is-active {
		border-color: rgba(180, 82, 40, 0.45);
		box-shadow: inset 0 0 0 1px rgba(180, 82, 40, 0.12);
	}

	.saved-title {
		font-size: 16px;
	}

	.saved-meta {
		overflow-wrap: anywhere;
	}

	.saved-time {
		white-space: nowrap;
		flex-shrink: 0;
	}

	.saved-actions {
		margin-top: 14px;
	}

	.saved-top > div {
		min-width: 0;
	}

	.section-title {
		font-size: 22px;
	}

	.response-stats {
		display: flex;
		flex-wrap: wrap;
		gap: 8px 16px;
	}

	code {
		display: inline-block;
		padding: 2px 6px;
		border-radius: 999px;
		background: rgba(229, 215, 197, 0.46);
		font-size: 12px;
		color: #6a4f32;
		max-width: 100%;
		overflow-wrap: anywhere;
	}

	.editor-card,
	.saved-card {
		min-height: 100%;
	}

	.saved-card {
		position: sticky;
		top: 24px;
	}

	@media (max-width: 1180px) {
		.hero-card {
			grid-template-columns: 1fr;
			gap: 18px;
		}

		.hero-meta {
			grid-template-columns: 1fr;
		}

		.hero-actions {
			justify-self: start;
			justify-content: flex-start;
		}
	}

	@media (max-width: 920px) {
		.workspace-grid {
			grid-template-columns: 1fr;
		}

		.saved-card {
			position: static;
		}

		.saved-list {
			max-height: none;
			overflow: visible;
		}
	}

	@media (max-width: 640px) {
		.page-shell {
			padding-inline: 14px;
		}

		.auth-panel,
		.hero-card,
		.panel-card {
			border-radius: 22px;
		}

		.hero-actions,
		.action-row,
		.saved-actions,
		.response-head,
		.saved-top,
		.field-grid {
			flex-direction: column;
			align-items: stretch;
		}

		.field-grid {
			display: flex;
			gap: 0;
		}

		.saved-time {
			white-space: normal;
		}
	}
</style>
