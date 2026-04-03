<template>
	<section class="login-page">
		<div v-if="redirectModalVisible" class="message-modal-mask">
			<div class="message-modal">
				<p class="message-modal-title">提示</p>
				<p class="message-modal-copy">
					{{ redirectMessage }}，{{ redirectCountdown }} 秒后自动跳转......
				</p>
			</div>
		</div>

		<section class="hero">
			<div class="hero-glow hero-glow-top"></div>
			<div class="hero-glow hero-glow-bottom"></div>
			<div class="hero-backdrop hero-backdrop-left"></div>
			<div class="hero-backdrop hero-backdrop-right"></div>

			<div class="hero-copy">
				<p class="eyebrow">ADMIN ENTRY</p>
				<h1 class="headline">后台管理登录</h1>
				<p class="subhead">请输入后台口令，系统会校验人员身份与角色权限。</p>
			</div>

			<div class="login-card">
				<label class="field-label" for="admin-passcode-input">请输入后台口令</label>
				<div class="input-shell" :class="{ active: hasPasscode, error: showNoMatch }">
					<input
						id="admin-passcode-input"
						:value="passcode"
						class="text-input"
						type="text"
						maxlength="32"
						autocomplete="off"
						:disabled="isRedirecting"
						placeholder="请输入后台口令"
						@input="handlePasscodeInput"
					/>
				</div>

				<p class="field-tip">{{ helperText }}</p>

				<div v-if="matchedRecord" class="matched-card">
					<p class="field-label">已匹配人员</p>
					<input class="matched-input" type="text" :value="matchedRecord.name" disabled />
					<div class="matched-meta">
						<span>{{ matchedRoleLabel }}</span>
						<span>审核状态：{{ reviewStatusLabel }}</span>
					</div>
				</div>

				<div v-if="shouldShowHint && !matchedRecord" class="hint-panel">
					<p class="hint-title">提示</p>
					<p class="hint-copy">该入口仅支持后台账号登录，普通用户请使用用户登录页。</p>
				</div>

				<div class="hero-actions">
					<button
						class="hero-action-btn primary-btn"
						type="button"
						:disabled="isPrimaryDisabled"
						@click="handlePrimaryAction"
					>
						{{ primaryButtonText }}
					</button>
					<button class="hero-action-btn ghost-btn" type="button" @click="backToWelcome">
						返回欢迎页
					</button>
				</div>

				<div class="user-entry">
					<p class="user-entry-copy">普通用户请使用用户登录入口</p>
					<button class="user-entry-link" type="button" @click="goUserLogin">
						前往用户登录
					</button>
				</div>
			</div>
		</section>
	</section>
</template>

<script setup>
	import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
	import { useRouter } from 'vue-router'

	import { personnelUserService as personnelUser } from '@/api/modules/personnel-user'
	import { markPostLoginHandoff, validateStoredToken } from '@/utils/auth-guard'
	import {
		applyPersonnelLoginSession,
		getLoginProfileFromStorage,
		getLoginProfileUserRole,
		hasLoginProfileStorage,
		isAdminUserRole,
		LOGIN_PROFILE_HOME_PATHS
	} from '@/utils/login-cookie'

	const router = useRouter()
	const reviewStatusMap = {
		pending: '待审核',
		approved: '已通过',
		rejected: '已驳回'
	}
	const roleLabelMap = {
		0: '普通用户',
		1: '同工',
		2: '管理成员',
		3: '系统管理员'
	}

	const passcode = ref('')
	const matchedRecord = ref(null)
	const isLookingUp = ref(false)
	const isSubmitting = ref(false)
	const isRedirecting = ref(false)
	const redirectModalVisible = ref(false)
	const redirectCountdown = ref(3)
	const redirectMessage = ref('检测到后台账号')
	const helperText = ref('请输入后台口令进行匹配。')

	let lookupToken = 0
	let redirectTimeoutId = 0
	let redirectIntervalId = 0

	const hasPasscode = computed(() => !!passcode.value)
	const shouldShowHint = computed(() => hasPasscode.value)
	const showNoMatch = computed(
		() => hasPasscode.value && !isLookingUp.value && !matchedRecord.value && !isRedirecting.value
	)
	const reviewStatusLabel = computed(() => {
		const reviewStatus = matchedRecord.value?.review_status || ''
		return reviewStatusMap[reviewStatus] || '未设置'
	})
	const matchedRoleLabel = computed(() => {
		const role = Number(matchedRecord.value?.user_role)
		return `角色：${roleLabelMap[role] || '未知角色'}`
	})
	const primaryButtonText = computed(() => (matchedRecord.value ? '确认进入后台' : '确认'))
	const isPrimaryDisabled = computed(() => {
		if (isLookingUp.value || isSubmitting.value || isRedirecting.value) {
			return true
		}

		if (!matchedRecord.value) {
			return !hasPasscode.value
		}

		return matchedRecord.value.review_status !== 'approved'
	})

	async function verifyStoredProfile(profile) {
		if (!hasLoginProfileStorage(profile)) {
			return null
		}

		try {
			const validatedUser = await validateStoredToken()
			if (!validatedUser) {
				return null
			}

			return getLoginProfileFromStorage()
		} catch (error) {
			return null
		}
	}

	async function redirectByStoredProfile() {
		const verifiedProfile = await verifyStoredProfile(getLoginProfileFromStorage())
		const userRole = getLoginProfileUserRole(verifiedProfile)
		if (!hasLoginProfileStorage(verifiedProfile) || userRole == null) {
			return
		}

		const targetPath = isAdminUserRole(userRole)
			? LOGIN_PROFILE_HOME_PATHS.admin
			: LOGIN_PROFILE_HOME_PATHS.user

		if (!targetPath || router.currentRoute.value.path === targetPath) {
			return
		}

		isRedirecting.value = true
		redirectModalVisible.value = true
		redirectCountdown.value = 3
		redirectMessage.value = isAdminUserRole(userRole) ? '检测到后台账号' : '检测到普通用户账号'
		helperText.value = `${redirectMessage.value}，3 秒后自动跳转......`

		redirectIntervalId = window.setInterval(() => {
			if (redirectCountdown.value > 1) {
				redirectCountdown.value -= 1
			}
		}, 1000)

		await new Promise((resolve) => {
			redirectTimeoutId = window.setTimeout(resolve, 3000)
		})

		clearRedirectTimers()
		await router.replace(targetPath)
	}

	function clearRedirectTimers() {
		if (redirectTimeoutId) {
			window.clearTimeout(redirectTimeoutId)
			redirectTimeoutId = 0
		}

		if (redirectIntervalId) {
			window.clearInterval(redirectIntervalId)
			redirectIntervalId = 0
		}
	}

	function normalizePasscode(value) {
		return String(value || '')
			.trim()
			.toUpperCase()
			.slice(0, 32)
	}

	function handlePasscodeInput(event) {
		const nextValue = normalizePasscode(event?.target?.value)
		passcode.value = nextValue
		matchedRecord.value = null

		if (!nextValue) {
			helperText.value = '请输入后台口令进行匹配。'
			return
		}

		helperText.value = '点击下方确认按钮后，将匹配对应后台人员信息。'
	}

	async function lookupMatchedRecord() {
		if (!passcode.value) {
			helperText.value = '请先输入后台口令。'
			return
		}

		const currentToken = ++lookupToken
		isLookingUp.value = true
		helperText.value = '正在匹配后台人员信息...'

		try {
			const result = await personnelUser.getLoginProfileByPasscode({
				passcode: passcode.value
			})

			if (currentToken !== lookupToken) {
				return
			}

			matchedRecord.value = result?.record || null
			if (!matchedRecord.value) {
				helperText.value = '未找到对应口令，请检查后重新输入。'
			} else if (!isAdminUserRole(matchedRecord.value.user_role)) {
				helperText.value = '当前口令为普通用户账号，请前往用户登录页。'
			} else {
				helperText.value = '已匹配后台账号，请确认姓名后继续。'
			}
		} catch (error) {
			if (currentToken !== lookupToken) {
				return
			}

			matchedRecord.value = null
			helperText.value = error?.message || '口令校验失败，请稍后重试。'
		} finally {
			if (currentToken === lookupToken) {
				isLookingUp.value = false
			}
		}
	}

	async function confirmLogin() {
		if (!matchedRecord.value) {
			helperText.value = '请先输入正确口令。'
			return
		}

		if (matchedRecord.value.review_status !== 'approved') {
			helperText.value = `当前状态为${reviewStatusLabel.value}，暂时无法进入。`
			return
		}

		if (!isAdminUserRole(matchedRecord.value.user_role)) {
			helperText.value = '当前口令为普通用户账号，请前往用户登录页。'
			return
		}

		isSubmitting.value = true

		try {
			const result = await personnelUser.loginByPasscode({
				passcode: passcode.value,
				personnelId: matchedRecord.value._id,
				personId: matchedRecord.value.person_id,
				name: matchedRecord.value.name,
				nickname: matchedRecord.value.nickname
			})

			applyPersonnelLoginSession({
				profile: result?.profile || matchedRecord.value,
				accessToken: result?.access_token || '',
				tokenType: result?.token_type || 'bearer'
			})
			markPostLoginHandoff(LOGIN_PROFILE_HOME_PATHS.admin)

			await router.replace(LOGIN_PROFILE_HOME_PATHS.admin)
		} catch (error) {
			helperText.value = error?.message || '登录确认失败，请稍后重试。'
		} finally {
			isSubmitting.value = false
		}
	}

	async function handlePrimaryAction() {
		if (matchedRecord.value) {
			await confirmLogin()
			return
		}

		await lookupMatchedRecord()
	}

	function backToWelcome() {
		router.push('/welcome')
	}

	function goUserLogin() {
		router.push(LOGIN_PROFILE_HOME_PATHS.login)
	}

	onMounted(async () => {
		await redirectByStoredProfile()
	})

	onBeforeUnmount(() => {
		clearRedirectTimers()
	})
</script>

<style scoped lang="less">
	.message-modal-mask {
		position: absolute;
		inset: 0;
		z-index: 20;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 24px;
		background: rgba(17, 24, 39, 0.28);
		backdrop-filter: blur(10px);
	}

	.message-modal {
		width: min(100%, 320px);
		padding: 28px 24px;
		border-radius: 28px;
		background: rgba(255, 255, 255, 0.96);
		box-shadow: 0 24px 48px rgba(31, 41, 55, 0.18);
		text-align: center;
	}

	.message-modal-title {
		margin: 0;
		font-size: 20px;
		font-weight: 700;
		color: #111827;
	}

	.message-modal-copy {
		margin: 14px 0 0;
		font-size: 15px;
		line-height: 1.8;
		color: #4b5563;
	}

	.login-page {
		min-height: 100vh;
		padding: 0;
		position: relative;
		background:
			radial-gradient(circle at top left, rgba(149, 204, 255, 0.35), transparent 30%),
			radial-gradient(circle at 85% 16%, rgba(125, 170, 255, 0.32), transparent 24%),
			radial-gradient(circle at 45% 62%, rgba(255, 255, 255, 0.78), transparent 34%),
			linear-gradient(180deg, #f6faff 0%, #eef4ff 44%, #f8fbff 100%);
	}

	.hero {
		position: relative;
		overflow: hidden;
		min-height: 100vh;
		padding: calc(56px + var(--safe-top, 0px)) clamp(22px, 5vw, 52px)
			calc(40px + var(--safe-bottom, 0px));
		background:
			linear-gradient(145deg, rgba(255, 255, 255, 0.7), rgba(242, 247, 255, 0.45)),
			linear-gradient(180deg, rgba(255, 255, 255, 0.24), rgba(255, 255, 255, 0.1));
		backdrop-filter: blur(18px);
		display: flex;
		flex-direction: column;
		justify-content: center;
	}

	.hero-glow {
		position: absolute;
		border-radius: 999px;
		filter: blur(10px);
		pointer-events: none;
	}

	.hero-glow-top {
		width: 260px;
		height: 260px;
		top: -120px;
		right: 10%;
		background: radial-gradient(circle, rgba(187, 219, 255, 0.86), transparent 72%);
	}

	.hero-glow-bottom {
		width: 280px;
		height: 280px;
		left: -90px;
		bottom: -120px;
		background: radial-gradient(circle, rgba(140, 174, 245, 0.34), transparent 72%);
	}

	.hero-backdrop {
		position: absolute;
		border-radius: 999px;
		filter: blur(10px);
		opacity: 0.55;
	}

	.hero-backdrop-left {
		width: 180px;
		height: 180px;
		left: -74px;
		top: -18px;
		background: linear-gradient(180deg, #b5d2ff 0%, #7ea9f5 100%);
	}

	.hero-backdrop-right {
		width: 164px;
		height: 164px;
		right: -52px;
		top: 146px;
		background: linear-gradient(180deg, #d2e4ff 0%, #a8c5f8 100%);
	}

	.hero-copy,
	.login-card {
		position: relative;
		z-index: 2;
	}

	.hero-copy {
		position: absolute;
		top: calc(57px + var(--safe-top, 0px));
		left: clamp(22px, 5vw, 52px);
		right: clamp(22px, 5vw, 52px);
	}

	.eyebrow {
		display: block;
		color: #30456e;
		letter-spacing: 0.24em;
		text-transform: uppercase;
		font-size: 12px;
		font-weight: 700;
	}

	.headline {
		max-width: 9em;
		margin: 14px 0 0;
		color: #111827;
		font-family: var(--font-display);
		font-size: clamp(38px, 7vw, 60px);
		line-height: 1.04;
		letter-spacing: 0.01em;
	}

	.subhead {
		margin: 18px 0 0;
		font-size: 17px;
		line-height: 1.75;
		color: #4b5563;
	}

	.login-card {
		width: min(100%, 560px);
		margin: 28px auto 0;
		padding: 28px;
		border-radius: 32px;
	}

	.field-label {
		display: block;
		margin-bottom: 12px;
		color: #1f2937;
		font-size: 15px;
		font-weight: 700;
	}

	.input-shell {
		display: flex;
		align-items: center;
		height: 58px;
		padding: 0 18px;
		border-radius: 999px;
		border: 1px solid rgba(59, 80, 116, 0.14);
		background: rgba(255, 255, 255, 0.92);
		transition:
			border-color 0.2s ease,
			box-shadow 0.2s ease;
	}

	.input-shell.active {
		border-color: rgba(43, 79, 146, 0.3);
		box-shadow: 0 12px 24px rgba(43, 79, 146, 0.09);
	}

	.input-shell.error {
		border-color: rgba(192, 100, 84, 0.34);
	}

	.text-input,
	.matched-input {
		width: 100%;
		border: none;
		outline: none;
		background: transparent;
		font-size: 16px;
		color: #1f2937;
	}

	.field-tip {
		min-height: 24px;
		margin: 12px 0 0;
		font-size: 13px;
		line-height: 1.7;
		color: #496082;
	}

	.matched-card {
		margin-top: 18px;
		padding: 18px;
		border-radius: 24px;
		background: linear-gradient(180deg, rgba(245, 249, 255, 0.96), rgba(234, 242, 255, 0.88));
		border: 1px solid rgba(68, 97, 143, 0.1);
	}

	.matched-input {
		height: 52px;
		padding: 0 16px;
		border-radius: 16px;
		background: rgba(255, 255, 255, 0.95);
		color: #111827;
		font-weight: 700;
		cursor: not-allowed;
	}

	.matched-meta {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
		margin-top: 12px;
	}

	.matched-meta span {
		display: inline-flex;
		align-items: center;
		min-height: 32px;
		padding: 0 12px;
		border-radius: 999px;
		background: rgba(255, 255, 255, 0.82);
		color: #35507b;
		font-size: 12px;
		font-weight: 600;
	}

	.hint-panel {
		margin-top: 18px;
		padding: 16px 18px;
		border-radius: 22px;
		background: rgba(55, 85, 139, 0.08);
	}

	.hint-title {
		margin: 0;
		color: #1f2937;
		font-size: 14px;
		font-weight: 700;
	}

	.hint-copy {
		margin: 8px 0 0;
		color: #4b5563;
		font-size: 14px;
		line-height: 1.75;
	}

	.hero-actions {
		display: flex;
		gap: 14px;
		margin-top: 22px;
	}

	.hero-action-btn {
		flex: 1;
		min-height: 56px;
		padding: 0 24px;
		border-radius: 999px;
		border: none;
		font-size: 16px;
		font-weight: 700;
		letter-spacing: 0.04em;
		transition:
			transform 0.25s ease,
			box-shadow 0.25s ease,
			filter 0.25s ease,
			opacity 0.25s ease;
		cursor: pointer;
	}

	.primary-btn {
		background: linear-gradient(135deg, #1f3458 0%, #29487d 55%, #2f5a95 100%);
		color: #eef5ff;
		box-shadow: 0 20px 36px rgba(40, 67, 112, 0.24);
	}

	.ghost-btn {
		background: rgba(255, 255, 255, 0.74);
		color: #34455f;
		border: 1px solid rgba(59, 80, 116, 0.14);
	}

	.hero-action-btn:hover:not(:disabled) {
		transform: translateY(-2px);
		filter: saturate(1.06);
	}

	.hero-action-btn:disabled {
		opacity: 0.48;
		cursor: not-allowed;
		box-shadow: none;
	}

	.user-entry {
		margin-top: 14px;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
	}

	.user-entry-copy {
		margin: 0;
		color: #4b5563;
		font-size: 13px;
	}

	.user-entry-link {
		border: none;
		background: transparent;
		color: #2f5a95;
		font-size: 13px;
		font-weight: 700;
		text-decoration: underline;
		cursor: pointer;
	}

	@media (max-width: 640px) {
		.hero {
			padding-left: 18px;
			padding-right: 18px;
		}

		.hero-copy {
			left: 18px;
			right: 18px;
		}

		.hero-actions {
			flex-direction: column;
		}

		.user-entry {
			flex-direction: column;
			gap: 4px;
		}

		.login-card {
			padding: 22px 18px;
		}

		.matched-meta {
			gap: 8px;
		}
	}
</style>
