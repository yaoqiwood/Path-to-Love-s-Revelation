<template>
	<section class="login-page">
		<section class="hero">
			<div class="hero-glow hero-glow-top"></div>
			<div class="hero-glow hero-glow-bottom"></div>
			<div class="hero-backdrop hero-backdrop-left"></div>
			<div class="hero-backdrop hero-backdrop-right"></div>

			<div class="hero-copy">
				<p class="eyebrow">PATH TO LOVE</p>
				<h1 class="headline">确认你的登录信息</h1>
				<p class="subhead">请输入口令，系统会自动匹配对应人员姓名。</p>
			</div>

			<div class="login-card">
				<label class="field-label" for="passcode-input">请输入口令</label>
				<div class="input-shell" :class="{ active: hasPasscode, error: showNoMatch }">
					<input
						id="passcode-input"
						:value="passcode"
						class="text-input"
						type="text"
						maxlength="32"
						autocomplete="off"
						placeholder="请输入口令"
						@input="handlePasscodeInput"
					/>
				</div>

				<p class="field-tip">{{ helperText }}</p>

				<div v-if="matchedRecord" class="matched-card">
					<p class="field-label">已匹配人员</p>
					<input class="matched-input" type="text" :value="matchedRecord.name" disabled />
				</div>

				<div v-if="shouldShowHint && !matchedRecord" class="hint-panel">
					<p class="hint-title">提示</p>
					<p class="hint-copy">口令正确后，点击确认后下方会显示匹配到的人员姓名，确认无误后即可继续。</p>
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
			</div>
		</section>
	</section>
</template>

<script setup>
	import { computed, ref } from 'vue'
	import { useRouter } from 'vue-router'

	import { personnelUserService as personnelUser } from '@/api/modules/personnel-user'
	import { applyMockPersonnelLogin } from '@/platform/mock-presets'

	const router = useRouter()
	const reviewStatusMap = {
		pending: '待审核',
		approved: '已通过',
		rejected: '已驳回'
	}

	const passcode = ref('')
	const matchedRecord = ref(null)
	const isLookingUp = ref(false)
	const isSubmitting = ref(false)
	const helperText = ref('请输入口令进行匹配。')

	let lookupToken = 0

	const hasPasscode = computed(() => !!passcode.value)
	const shouldShowHint = computed(() => hasPasscode.value)
	const showNoMatch = computed(
		() => hasPasscode.value && !isLookingUp.value && !matchedRecord.value
	)
	const reviewStatusLabel = computed(() => {
		const reviewStatus = matchedRecord.value?.review_status || ''
		return reviewStatusMap[reviewStatus] || '未设置'
	})
	const primaryButtonText = computed(() => (matchedRecord.value ? '确认进入' : '确认'))
	const isPrimaryDisabled = computed(() => {
		if (isLookingUp.value || isSubmitting.value) {
			return true
		}

		if (!matchedRecord.value) {
			return !hasPasscode.value
		}

		return matchedRecord.value.review_status !== 'approved'
	})

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
			helperText.value = '请输入口令进行匹配。'
			return
		}

		helperText.value = '点击下方确认按钮后，将匹配对应人员信息。'
	}

	async function lookupMatchedRecord() {
		if (!passcode.value) {
			helperText.value = '请先输入口令。'
			return
		}

		const currentToken = ++lookupToken
		isLookingUp.value = true
		helperText.value = '正在匹配人员信息...'

		try {
			const result = await personnelUser.getLoginProfileByPasscode({
				passcode: passcode.value
			})

			if (currentToken !== lookupToken) {
				return
			}

			matchedRecord.value = result?.record || null
			helperText.value = matchedRecord.value
				? '已匹配到人员信息，请确认姓名后继续。'
				: '未找到对应口令，请检查后重新输入。'
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

		isSubmitting.value = true

		try {
			applyMockPersonnelLogin({
				...matchedRecord.value
			})
			await router.replace('/pages/index/home')
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
</script>

<style scoped lang="less">
	.login-page {
		min-height: 100vh;
		padding: 0;
		background:
			radial-gradient(circle at top left, rgba(255, 204, 177, 0.48), transparent 30%),
			radial-gradient(circle at 85% 16%, rgba(170, 221, 255, 0.38), transparent 22%),
			radial-gradient(circle at 50% 52%, rgba(255, 255, 255, 0.78), transparent 34%),
			linear-gradient(180deg, #fffaf5 0%, #fff2e8 44%, #fff8f1 100%);
	}

	.hero {
		position: relative;
		overflow: hidden;
		min-height: 100vh;
		padding: calc(56px + var(--safe-top, 0px)) clamp(22px, 5vw, 52px)
			calc(40px + var(--safe-bottom, 0px));
		background:
			linear-gradient(145deg, rgba(255, 255, 255, 0.7), rgba(255, 247, 240, 0.4)),
			linear-gradient(180deg, rgba(255, 255, 255, 0.22), rgba(255, 255, 255, 0.08));
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
		right: 12%;
		background: radial-gradient(circle, rgba(255, 228, 210, 0.88), transparent 72%);
	}

	.hero-glow-bottom {
		width: 280px;
		height: 280px;
		left: -90px;
		bottom: -120px;
		background: radial-gradient(circle, rgba(255, 203, 164, 0.42), transparent 72%);
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
		background: linear-gradient(180deg, #ffd5bc 0%, #ffb58b 100%);
	}

	.hero-backdrop-right {
		width: 164px;
		height: 164px;
		right: -52px;
		top: 146px;
		background: linear-gradient(180deg, #cbe8ff 0%, #8ec8ff 100%);
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
		color: #8d5d41;
		letter-spacing: 0.28em;
		text-transform: uppercase;
		font-size: 12px;
		font-weight: 700;
	}

	.headline {
		max-width: 9em;
		margin: 14px 0 0;
		color: #2b1d19;
		font-family: var(--font-display);
		font-size: clamp(38px, 7vw, 60px);
		line-height: 1.04;
		letter-spacing: 0.01em;
	}

	.subhead {
		margin: 18px 0 0;
		font-size: 17px;
		line-height: 1.75;
		color: #6d5b56;
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
		color: #3f2d26;
		font-size: 15px;
		font-weight: 700;
	}

	.input-shell {
		display: flex;
		align-items: center;
		height: 58px;
		padding: 0 18px;
		border-radius: 999px;
		border: 1px solid rgba(94, 68, 54, 0.12);
		background: rgba(255, 255, 255, 0.9);
		transition:
			border-color 0.2s ease,
			box-shadow 0.2s ease;
	}

	.input-shell.active {
		border-color: rgba(91, 76, 136, 0.28);
		box-shadow: 0 12px 24px rgba(91, 76, 136, 0.08);
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
		color: #342925;
	}

	.field-tip {
		min-height: 24px;
		margin: 12px 0 0;
		font-size: 13px;
		line-height: 1.7;
		color: #876b60;
	}

	.matched-card {
		margin-top: 18px;
		padding: 18px;
		border-radius: 24px;
		background: linear-gradient(180deg, rgba(255, 248, 243, 0.96), rgba(255, 242, 232, 0.86));
		border: 1px solid rgba(118, 84, 63, 0.08);
	}

	.matched-input {
		height: 52px;
		padding: 0 16px;
		border-radius: 16px;
		background: rgba(255, 255, 255, 0.92);
		color: #2f211d;
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
		background: rgba(255, 255, 255, 0.8);
		color: #765446;
		font-size: 12px;
		font-weight: 600;
	}

	.hint-panel {
		margin-top: 18px;
		padding: 16px 18px;
		border-radius: 22px;
		background: rgba(47, 42, 71, 0.06);
	}

	.hint-title {
		margin: 0;
		color: #3f2d26;
		font-size: 14px;
		font-weight: 700;
	}

	.hint-copy {
		margin: 8px 0 0;
		color: #6f615c;
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
		background: linear-gradient(135deg, #2f2a47 0%, #5b4c88 55%, #7b5f83 100%);
		color: #fff9f0;
		box-shadow: 0 20px 36px rgba(77, 62, 109, 0.26);
	}

	.ghost-btn {
		background: rgba(255, 255, 255, 0.72);
		color: #4e3d37;
		border: 1px solid rgba(94, 68, 54, 0.12);
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

		.login-card {
			padding: 22px 18px;
		}

		.matched-meta {
			gap: 8px;
		}
	}
</style>
