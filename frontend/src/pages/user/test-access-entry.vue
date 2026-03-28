<template>
	<view class="page">
		<view v-if="shouldShowProfilePopup" class="profile-mask" @click="closeProfilePopup">
			<view class="profile-dialog" @click.stop>
				<text class="profile-close" @click="closeProfilePopup">×</text>
				<text class="profile-title">请先完善资料</text>
				<text class="profile-desc">进入测试前，请填写昵称并上传头像。</text>

				<view class="profile-avatar-wrap">
					<view class="profile-avatar-trigger" @click="chooseAvatarImage">
						<image
							v-if="profileForm.avatar"
							class="profile-avatar"
							:src="profileForm.avatar"
							mode="aspectFill"
						></image>
						<view v-else class="profile-avatar profile-avatar-empty">
							<text>头像</text>
						</view>
					</view>
				</view>

				<button class="profile-picker-btn" @click="chooseAvatarImage">选择头像</button>

				<view class="profile-input-shell">
					<input
						v-model="profileForm.nickname"
						class="profile-input"
						type="text"
						placeholder="请输入昵称"
						confirm-type="done"
					/>
				</view>

				<button class="profile-confirm-btn" @click="confirmProfile">确认资料</button>
			</view>
		</view>

		<view class="hero">
			<view class="hero-backdrop hero-backdrop-left"></view>
			<view class="hero-backdrop hero-backdrop-right"></view>
			<view class="hero-copy" @click="handleHeroCopyTap">
				<text class="eyebrow">LOVE MBTI LAB</text>
				<text class="headline">信息确认</text>
			</view>

			<view class="form-card">
				<view v-if="shouldShowInviteCodeField" class="field-block">
					<text class="field-label">邀请码</text>
					<view class="input-shell">
						<input
							v-model="password"
							class="text-input"
							type="text"
							maxlength="32"
							@input="handlePasswordInput"
							placeholder="请输入邀请码（如没有可不填）"
							confirm-type="done"
						/>
					</view>
				</view>

				<view :class="['action-row', { 'action-row-stacked': !shouldShowInviteCodeField }]">
					<view class="action-btn primary-btn" @click="handlePrimaryAction">
						<text>{{ shouldShowInviteCodeField ? '确认' : '进入测试' }}</text>
					</view>
					<view class="action-btn ghost-btn" @click="goHome">
						<text>返回首页</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	const personnelUser = uniCloud.importObject('personnel-user')
	const PERSONNEL_PROFILE_STORAGE_KEY = 'mbtiPersonnelProfile'

	export default {
		data() {
			return {
				nameOptions: [],
				nameInput: '',
				selectedName: '',
				selectedRecord: null,
				matchedOpenidRecord: null,
				loginOpenIds: [],
				password: '',
				showNameOptions: false,
				showProfilePopup: false,
				saving: false,
				lastErrorMessage: '',
				lastErrorAt: 0,
				autoRoutedByOpenid: false,
				hasPromptedRetest: false,
				currentUser: null,
				restoredByOpenid: false,
				helperPageReviewMode: true,
				inviteCodeTapCount: 0,
				lastInviteCodeTapAt: 0,
				inviteCodeUnlocked: false,
				profileForm: {
					nickname: '',
					avatar: ''
				}
			}
		},
		async onLoad() {
			await this.loadCurrentUser()
			await this.loadSystemConfig()
			await this.initOpenidProfileState()
		},
		computed: {
			filteredNames() {
				return this.nameOptions
			},
			shouldShowProfilePopup() {
				return this.showProfilePopup
			},
			shouldShowInviteCodeField() {
				return !this.helperPageReviewMode && this.inviteCodeUnlocked
			}
		},
		methods: {
			async loadSystemConfig() {
				try {
					const result = await personnelUser.getSystemConfig({
						configCode: 'default'
					})
					const config = (result && result.config) || {}
					this.helperPageReviewMode = !!config.helper_page_review_mode
					if (this.helperPageReviewMode) {
						this.inviteCodeUnlocked = false
						this.password = ''
					}
				} catch (error) {
					console.error('loadSystemConfig failed', error)
					this.helperPageReviewMode = true
					this.inviteCodeUnlocked = false
					this.password = ''
				}
			},
			handleHeroCopyTap() {
				const now = Date.now()
				if (now - this.lastInviteCodeTapAt > 1200) {
					this.inviteCodeTapCount = 0
				}
				this.lastInviteCodeTapAt = now
				this.inviteCodeTapCount += 1
				if (this.inviteCodeTapCount < 5) {
					return
				}
				this.inviteCodeTapCount = 0
				if (this.helperPageReviewMode) {
					return
				}
				this.inviteCodeUnlocked = true
			},
			handlePrimaryAction() {
				if (!this.shouldShowInviteCodeField) {
					this.password = ''
					this.enterTestDirectly()
					return
				}
				this.submitForm()
			},
			savePersonnelProfileToStorage(payload) {
				try {
					uni.setStorageSync(PERSONNEL_PROFILE_STORAGE_KEY, {
						...payload,
						cached_at: Date.now()
					})
				} catch (error) {
					console.error('savePersonnelProfileToStorage failed', error)
				}
			},
			getCandidateOpenIds(user = {}) {
				const wxOpenid = user && user.wx_openid
				if (!wxOpenid) {
					return []
				}
				if (typeof wxOpenid === 'string') {
					const value = wxOpenid.trim()
					return value ? [value] : []
				}
				if (typeof wxOpenid !== 'object') {
					return []
				}

				const preferredKeys = ['mp-weixin', 'mp_weixin', 'mp', 'weixin']
				const values = preferredKeys
					.map((key) => wxOpenid[key])
					.concat(Object.values(wxOpenid || {}))
					.map((item) => (typeof item === 'string' ? item.trim() : ''))
					.filter(Boolean)

				return Array.from(new Set(values))
			},
			getLoginOpenId(user = {}) {
				return this.getCandidateOpenIds(user)[0] || ''
			},
			buildPersonnelProfilePayload(record = {}) {
				return {
					...record,
					id: record._id || '',
					personnel_id: record._id || '',
					person_id: typeof record.person_id !== 'undefined' ? record.person_id : '',
					user_role: Number(record.user_role) || 0,
					name: record.name || '',
					nickname: record.nickname || '',
					passcode: record.passcode || '',
					personal_photo: record.personal_photo || '',
					user_id: record.user_id || '',
					wx_openid: record.wx_openid || '',
					wx_unionid: record.wx_unionid || '',
					wx_nickname: record.wx_nickname || '',
					wx_avatar: record.wx_avatar || ''
				}
			},
			hasMbtiResult(record = {}) {
				return !!String(record.mbti || '')
					.trim()
					.toUpperCase()
			},
			hasNicknameAndAvatar(record = {}) {
				const nickname = String(record.nickname || '').trim()
				const avatar = String(record.wx_avatar || record.personal_photo || '').trim()
				return !!(nickname && avatar)
			},
			hasNameAndPasscode(record = {}) {
				const name = String(record.name || '').trim()
				const passcode = String(record.passcode || '').trim()
				return !!(name && passcode)
			},
			shouldAutoRouteToTest(record = {}) {
				return (
					this.hasNicknameAndAvatar(record) &&
					this.hasNameAndPasscode(record) &&
					!this.hasMbtiResult(record)
				)
			},
			hasBoundMbtiRecord(record = {}) {
				return this.hasNameAndPasscode(record) && this.hasMbtiResult(record)
			},
			promptRetestForBoundRecord(record = {}) {
				if (!record || !record._id || this.hasPromptedRetest) {
					return
				}

				this.hasPromptedRetest = true
				this.savePersonnelProfileToStorage(this.buildPersonnelProfilePayload(record))
				uni.showModal({
					title: '提示',
					content: '当前已经检测到您已有MBTI信息，是否重测？',
					confirmText: '是',
					cancelText: '否',
					success: (res) => {
						if (res.confirm) {
							const fastOpenid =
								this.loginOpenIds[0] || this.getLoginOpenId(this.currentUser || {})
							uni.reLaunch({
								url:
									`/pages/feed/entry?name=${encodeURIComponent(record.name || '')}` +
									`&personnelId=${encodeURIComponent(record._id || '')}` +
									`&wxOpenid=${encodeURIComponent(fastOpenid || '')}`
							})
							return
						}
						uni.reLaunch({
							url: '/pages/index/index'
						})
					},
					fail: () => {
						this.hasPromptedRetest = false
					}
				})
			},
			routeToTestByRecord(record = {}) {
				if (!record || !record._id || this.autoRoutedByOpenid) {
					return false
				}
				this.savePersonnelProfileToStorage(this.buildPersonnelProfilePayload(record))
				this.autoRoutedByOpenid = true
				const fastOpenid = this.loginOpenIds[0] || this.getLoginOpenId(this.currentUser || {})
				uni.showToast({
					title: '检测到已绑定资料，正在进入测试',
					icon: 'none',
					duration: 1200
				})
				setTimeout(() => {
					uni.reLaunch({
						url:
							`/pages/feed/entry?name=${encodeURIComponent(record.name || '')}` +
							`&personnelId=${encodeURIComponent(record._id || '')}` +
							`&wxOpenid=${encodeURIComponent(fastOpenid || '')}`
					})
				}, 260)
				return true
			},
			async loadCurrentUser() {
				try {
					const currentUserInfo = uniCloud.getCurrentUserInfo()
					const cachedUser = uni.getStorageSync('uni-id-pages-userInfo') || {}
					const currentUserInfoUser = currentUserInfo.userInfo || {}
					const user = {
						...currentUserInfoUser,
						...cachedUser,
						_id: currentUserInfo.uid || cachedUser._id || '',
						wx_openid:
							cachedUser.wx_openid ||
							currentUserInfoUser.wx_openid ||
							currentUserInfo.wx_openid ||
							'',
						wx_unionid:
							cachedUser.wx_unionid ||
							currentUserInfoUser.wx_unionid ||
							currentUserInfo.wx_unionid ||
							''
					}
					this.currentUser = user
					this.profileForm.nickname = user.nickname || ''
					this.profileForm.avatar =
						(user.avatar_file && user.avatar_file.url) || user.avatar_file || user.avatar || ''
					console.log('[access-form] loadCurrentUser', {
						currentUserInfo,
						cachedUser,
						user
					})
				} catch (error) {
					console.error('[access-form] loadCurrentUser failed', error)
				}
			},
			async fetchLoginOpenIdsFromServer() {
				try {
					const uid =
						(this.currentUser && this.currentUser._id) || (uniCloud.getCurrentUserInfo() || {}).uid || ''
					const result = await personnelUser.getCurrentLoginWxOpenid({
						uid
					})
					console.log('[access-form] getCurrentLoginWxOpenid result', result)
					return (result && result.openIds) || []
				} catch (error) {
					console.error('[access-form] getCurrentLoginWxOpenid failed', error)
					return []
				}
			},
			applyProfileFormBySources(record = null) {
				const user = this.currentUser || {}
				const recordNickname = String((record && record.nickname) || '').trim()
				const recordAvatar = String((record && (record.wx_avatar || record.personal_photo)) || '').trim()
				const userAvatar =
					(user.avatar_file && user.avatar_file.url) || user.avatar_file || user.avatar || ''

				this.profileForm.nickname = recordNickname || user.nickname || ''
				this.profileForm.avatar = recordAvatar || userAvatar || ''
			},
			async findPersonnelRecordByOpenIds(openIds = []) {
				if (!openIds.length) {
					return null
				}
				for (let i = 0; i < openIds.length; i++) {
					const result = await personnelUser.getByWxOpenid({
						wxOpenid: openIds[i]
					})
					if (result && result.record && result.record._id) {
						return result.record
					}
				}
				return null
			},
			async initOpenidProfileState() {
				try {
					let openIds = this.getCandidateOpenIds(this.currentUser)
					if (!openIds.length) {
						openIds = await this.fetchLoginOpenIdsFromServer()
					}
					this.loginOpenIds = openIds
					const record = await this.findPersonnelRecordByOpenIds(openIds)
					this.matchedOpenidRecord = record
					this.applyProfileFormBySources(record)
					if (record && record._id && record.name) {
						this.nameInput = record.name
						this.selectedName = record.name
						this.selectedRecord = {
							_id: record._id,
							name: record.name,
							user_role: Number(record.user_role) || 0
						}
					}
					this.showProfilePopup = !this.hasNicknameAndAvatar(record || {})
					if (this.showProfilePopup) {
						return
					}
					if (this.shouldAutoRouteToTest(record || {})) {
						this.routeToTestByRecord(record)
						return
					}
					if (this.hasBoundMbtiRecord(record || {})) {
						this.promptRetestForBoundRecord(record)
						return
					}
				} catch (error) {
					console.error('initOpenidProfileState failed', error)
					this.applyProfileFormBySources(null)
					this.syncProfilePopupState()
				}
			},
			syncProfilePopupState() {
				this.showProfilePopup = !(this.profileForm.nickname && this.profileForm.avatar)
			},
			async tryRestoreProfileByOpenid() {
				try {
					let openIds = this.getCandidateOpenIds(this.currentUser)
					if (!openIds.length) {
						openIds = await this.fetchLoginOpenIdsFromServer()
					}
					console.log('[access-form] tryRestoreProfileByOpenid openIds', openIds)
					if (!openIds.length) {
						console.log('[access-form] no openid found, skip restore')
						return false
					}

					let record = null
					for (let i = 0; i < openIds.length; i++) {
						console.log('[access-form] querying personnel by openid', openIds[i])
						const result = await personnelUser.getByWxOpenid({
							wxOpenid: openIds[i]
						})
						console.log('[access-form] getByWxOpenid result', {
							wxOpenid: openIds[i],
							result
						})
						if (result && result.record && result.record._id) {
							record = result.record
							break
						}
					}
					if (!record || !record._id) {
						console.log('[access-form] no personnel record matched openid')
						return false
					}
					if (this.shouldAutoRouteToTest(record)) {
						console.log('[access-form] personnel matched and bound without mbti, relaunch to test', record)
						this.routeToTestByRecord(record)
						return true
					}
					if (!this.hasMbtiResult(record)) {
						console.log('[access-form] personnel matched but no mbti result, stay on page', record)
						return false
					}

					console.log('[access-form] matched personnel record, relaunch to index', record)
					this.savePersonnelProfileToStorage(this.buildPersonnelProfilePayload(record))
					uni.showToast({
						title: '已有MBTI测试记录，正在进入首页',
						icon: 'none',
						duration: 1800
					})
					this.restoredByOpenid = true
					setTimeout(() => {
						uni.reLaunch({
							url: '/pages/index/index'
						})
					}, 500)
					return true
				} catch (error) {
					console.error('tryRestoreProfileByOpenid failed', error)
					return false
				}
			},
			onChooseAvatar(event) {
				const avatarUrl = event && event.detail && event.detail.avatarUrl
				if (avatarUrl) {
					this.profileForm.avatar = avatarUrl
				}
			},
			chooseAvatarImage() {
				uni.chooseImage({
					count: 1,
					sizeType: ['compressed'],
					sourceType: ['album', 'camera'],
					success: (res) => {
						const filePath = res.tempFilePaths && res.tempFilePaths[0]
						if (filePath) {
							this.profileForm.avatar = filePath
						}
					} 
				})
			},
			async confirmProfile() {
				if (!this.profileForm.nickname.trim()) {
					this.showProfilePopup = true
					this.showToastOnce('昵称不能为空')
					return
				}
				if (!this.profileForm.avatar) {
					this.showProfilePopup = true
					this.showToastOnce('请上传头像')
					return
				}
				let matchedRecord = this.matchedOpenidRecord
				try {
					if ((!matchedRecord || !matchedRecord._id) && this.loginOpenIds.length) {
						matchedRecord = await this.findPersonnelRecordByOpenIds(this.loginOpenIds)
						this.matchedOpenidRecord = matchedRecord
					}
				} catch (error) {
					console.error('confirmProfile query by openid failed', error)
				}
				if (matchedRecord && matchedRecord._id) {
					if (this.saving) {
						return
					}
					this.saving = true
					uni.showLoading({
						title: '保存中',
						mask: true
					})
					try {
						const nickname = this.profileForm.nickname.trim()
						const avatarFileId = await this.uploadAvatarIfNeeded()
						const user = this.currentUser || {}
						const loginOpenId =
							this.loginOpenIds[0] ||
							this.getLoginOpenId(user) ||
							String(matchedRecord.wx_openid || '').trim()
						const updateResult = await personnelUser.update({
							id: matchedRecord._id,
							data: {
								nickname: nickname,
								wx_openid: loginOpenId,
								wx_unionid: user.wx_unionid || matchedRecord.wx_unionid || '',
								wx_nickname: nickname,
								wx_avatar: avatarFileId
							}
						})
						const persistedRecord = {
							...matchedRecord,
							_id: (updateResult && updateResult.id) || matchedRecord._id,
							person_id:
								updateResult && typeof updateResult.person_id !== 'undefined'
									? updateResult.person_id
									: matchedRecord.person_id,
							user_role:
								updateResult && typeof updateResult.user_role !== 'undefined'
									? Number(updateResult.user_role) || 0
									: Number(matchedRecord.user_role) || 0,
							passcode:
								(updateResult && updateResult.passcode) || matchedRecord.passcode || '',
							nickname: nickname,
							personal_photo: matchedRecord.personal_photo || '',
							wx_openid: loginOpenId,
							wx_unionid: user.wx_unionid || matchedRecord.wx_unionid || '',
							wx_nickname: nickname,
							wx_avatar: avatarFileId
						}
						this.matchedOpenidRecord = persistedRecord
						this.savePersonnelProfileToStorage(this.buildPersonnelProfilePayload(persistedRecord))
						this.showProfilePopup = false
						if (this.hasMbtiResult(persistedRecord)) {
							this.promptRetestForBoundRecord(persistedRecord)
							return
						}
						if (!this.hasNameAndPasscode(persistedRecord)) {
							uni.showToast({
								title: '资料已同步',
								icon: 'none'
							})
							return
						}
						uni.showToast({
							title: '资料已同步，正在进入测试',
							icon: 'none'
						})
						setTimeout(() => {
							uni.navigateTo({
								url:
									`/pages/feed/entry?name=${encodeURIComponent(persistedRecord.name || '')}` +
									`&personnelId=${encodeURIComponent(persistedRecord._id || '')}` +
									`&wxOpenid=${encodeURIComponent(loginOpenId || '')}`
							})
						}, 350)
					} catch (error) {
						this.showProfilePopup = true
						this.showErrorModal((error && error.message) || '资料同步失败')
					} finally {
						this.saving = false
						uni.hideLoading()
					}
					return
				}
				if (false && matchedRecord && matchedRecord._id && this.hasNameAndPasscode(matchedRecord)) {
					this.savePersonnelProfileToStorage(
						this.buildPersonnelProfilePayload({
							...matchedRecord,
							nickname: this.profileForm.nickname.trim(),
							wx_avatar: this.profileForm.avatar
						})
					)
					uni.showToast({
						title: '已识别已绑定账号，正在进入测试',
						icon: 'none'
					})
					setTimeout(() => {
						const fastOpenid = this.loginOpenIds[0] || this.getLoginOpenId(this.currentUser || {})
						uni.navigateTo({
							url:
								`/pages/feed/entry?name=${encodeURIComponent(matchedRecord.name || '')}` +
								`&personnelId=${encodeURIComponent(matchedRecord._id || '')}` +
								`&wxOpenid=${encodeURIComponent(fastOpenid || '')}`
						})
					}, 350)
					return
				}
				this.showProfilePopup = false
			},
			closeProfilePopup() {
				this.showProfilePopup = false
			},
			async searchNameOptions(keyword) {
				try {
					const res = await personnelUser.searchNames({
						keyword: keyword || '',
						limit: 5
					})
					this.nameOptions = (res && res.list) || []
				} catch (error) {
					this.nameOptions = []
				}
			},
			async uploadAvatarIfNeeded() {
				const avatar = this.profileForm.avatar
				if (!avatar) {
					return ''
				}
				if (/^(cloud|https?:)/.test(avatar)) {
					return avatar
				}
				const ext = avatar.split('.').pop() || 'jpg'
				const uploadRes = await uniCloud.uploadFile({
					filePath: avatar,
					cloudPath:
						'mbti-personnel/avatar-' +
						Date.now() +
						'-' +
						Math.random().toString(36).slice(2) +
						'.' +
						ext
				})
				this.profileForm.avatar = uploadRes.fileID
				return uploadRes.fileID
			},
			handleNameFocus() {
				this.showNameOptions = true
				this.searchNameOptions(this.nameInput.trim())
			},
			handleNameInput(event) {
				this.nameInput = event.detail.value
				this.selectedName = ''
				this.selectedRecord = null
				this.showNameOptions = true
				this.searchNameOptions(this.nameInput.trim())
			},
			handleNameBlur() {
				setTimeout(() => {
					const value = this.nameInput.trim()
					if (this.selectedName && this.selectedName === value) {
						this.nameInput = value
					} else if (!this.nameOptions.some((item) => item.name === value)) {
						this.nameInput = ''
						this.selectedName = ''
						this.selectedRecord = null
					} else {
						this.nameInput = value
						this.selectedName = value
						this.selectedRecord =
							this.nameOptions.find((item) => item.name === value) || this.selectedRecord
					}
					this.showNameOptions = false
					this.nameOptions = []
				}, 120)
			},
			selectName(item) {
				this.nameInput = item.name
				this.selectedName = item.name
				this.selectedRecord = item
				this.showNameOptions = false
				this.nameOptions = []
			},
			handlePasswordInput(event) {
				const value = String((event && event.detail && event.detail.value) || '')
					.trim()
					.slice(0, 32)
				this.password = value
			},
			shouldSkipFeedback(message) {
				const content = String(message || '').trim()
				const now = Date.now()
				if (!content) {
					return false
				}
				if (this.lastErrorMessage === content && now - this.lastErrorAt < 1500) {
					return true
				}
				this.lastErrorMessage = content
				this.lastErrorAt = now
				return false
			},
			showToastOnce(message) {
				const content = String(message || '').trim()
				if (!content || this.shouldSkipFeedback(content)) {
					return
				}
				uni.showToast({
					title: content,
					icon: 'none'
				})
			},
			showErrorModal(message) {
				const content = message || '保存失败'
				if (this.shouldSkipFeedback(content)) {
					return
				}
				uni.showModal({
					content: content,
					showCancel: false
				})
			},
			isInviteCodeInvalidFeedback(payload = {}) {
				const code = String(payload.code || payload.errCode || '')
					.trim()
					.toUpperCase()
				const message = String(payload.message || payload.errMsg || '')
					.trim()
					.toLowerCase()
				if (code === 'INVALID_INVITE_CODE' || code === 'INVALID_PASSCODE') {
					return true
				}
				return (
					message.includes('邀请码无效') ||
					message.includes('邀请码错误') ||
					message.includes('口令无效') ||
					message.includes('口令错误') ||
					message.includes('invalid invite code') ||
					message.includes('invalid passcode')
				)
			},
			async submitForm() {
				if (this.shouldShowProfilePopup) {
					uni.showToast({
						title: '请先填写昵称和头像',
						icon: 'none'
					})
					return
				}
				if (this.hasBoundMbtiRecord(this.matchedOpenidRecord || {})) {
					this.promptRetestForBoundRecord(this.matchedOpenidRecord || {})
					return
				}
				const inviteCode = this.password.trim()
				if (!inviteCode) {
					this.enterTestDirectly()
					return
				}
				if (this.saving) {
					return
				}

				this.saving = true
				uni.showLoading({
					title: '保存中',
					mask: true
				})

				try {
					const uid = uniCloud.getCurrentUserInfo().uid
					if (!uid) {
						throw new Error('请先完成微信登录')
					}

					const avatarFileId = await this.uploadAvatarIfNeeded()
					const user = this.currentUser || {}
					const loginOpenId = this.loginOpenIds[0] || this.getLoginOpenId(user)
					const result = await personnelUser.upsertByUser({
						userId: uid,
						data: {
							nickname: this.profileForm.nickname.trim(),
							passcode: inviteCode,
							user_id: uid,
							wx_openid: loginOpenId,
							wx_unionid: user.wx_unionid || '',
							wx_nickname: this.profileForm.nickname.trim(),
							wx_avatar: avatarFileId
						}
					})
					if (result && result.ok === false) {
						if (this.isInviteCodeInvalidFeedback(result || {})) {
							this.showErrorModal('邀请码填写错误，请联系相关人员')
							return
						}
						this.showErrorModal(result.message || '保存失败')
						return
					}
					if (
						!result ||
						result.matched === false ||
						result.updated === false ||
						(result.skipped === true && !result.id)
					) {
						this.showErrorModal('邀请码填写错误，请联系相关人员')
						return
					}
					const persistedRecord = {
						...(this.matchedOpenidRecord || {}),
						_id: (result && result.id) || '',
						person_id: result && typeof result.person_id !== 'undefined' ? result.person_id : '',
						user_role:
							result && typeof result.user_role !== 'undefined'
								? Number(result.user_role) || 0
								: Number(
										(this.matchedOpenidRecord && this.matchedOpenidRecord.user_role) || 0
								  ) || 0,
						name:
							(result && result.name) ||
							(this.matchedOpenidRecord && this.matchedOpenidRecord.name) ||
							'',
						nickname: this.profileForm.nickname.trim(),
						passcode: (result && result.passcode) || inviteCode,
						mbti:
							(result && result.mbti) ||
							(this.matchedOpenidRecord && this.matchedOpenidRecord.mbti) ||
							'',
						personal_photo:
							(result && result.personal_photo) ||
							(this.matchedOpenidRecord && this.matchedOpenidRecord.personal_photo) ||
							'',
						user_id: uid,
						wx_openid: (result && result.wx_openid) || loginOpenId || '',
						wx_unionid: user.wx_unionid || '',
						wx_nickname: this.profileForm.nickname.trim(),
						wx_avatar: (result && result.wx_avatar) || avatarFileId || ''
					}

					this.matchedOpenidRecord = persistedRecord
					this.savePersonnelProfileToStorage(this.buildPersonnelProfilePayload(persistedRecord))
					if (this.hasMbtiResult(persistedRecord)) {
						this.promptRetestForBoundRecord(persistedRecord)
						return
					}
					uni.showToast({
						title: '绑定成功，正在进入测试',
						icon: 'none'
					})
					setTimeout(() => {
						this.enterTestDirectly()
					}, 350)
				} catch (error) {
					if (this.isInviteCodeInvalidFeedback(error || {})) {
						this.showErrorModal('邀请码填写错误，请联系相关人员')
						return
					}
					this.showErrorModal((error && error.message) || '保存失败')
				} finally {
					this.saving = false
					uni.hideLoading()
				}
			},
			enterTestDirectly() {
				if (this.shouldShowProfilePopup) {
					uni.showToast({
						title: '请先填写昵称和头像',
						icon: 'none'
					})
					return
				}
				if (this.hasBoundMbtiRecord(this.matchedOpenidRecord || {})) {
					this.promptRetestForBoundRecord(this.matchedOpenidRecord || {})
					return
				}

				const targetRecord = this.matchedOpenidRecord || this.selectedRecord || {}
				const targetName = String(targetRecord.name || this.selectedName || this.nameInput || '').trim()
				const targetPersonnelId = String(targetRecord._id || '').trim()
				const targetWxOpenid = String(
					this.loginOpenIds[0] || this.getLoginOpenId(this.currentUser || {}) || ''
				).trim()

				let url = '/pages/feed/entry'
				const query = []
				if (targetName) {
					query.push(`name=${encodeURIComponent(targetName)}`)
				}
				if (targetPersonnelId) {
					query.push(`personnelId=${encodeURIComponent(targetPersonnelId)}`)
				}
				if (targetWxOpenid) {
					query.push(`wxOpenid=${encodeURIComponent(targetWxOpenid)}`)
				}
				if (query.length) {
					url += `?${query.join('&')}`
				}

				uni.navigateTo({
					url
				})
			},
			goHome() {
				uni.navigateTo({
					url: '/pages/index/service'
				})
			}
		}
	}
</script>

<style scoped lang="less">
	.page {
		min-height: 100vh;
		background:
			radial-gradient(circle at top left, rgba(255, 194, 159, 0.42), transparent 30%),
			radial-gradient(circle at top right, rgba(135, 202, 255, 0.4), transparent 24%),
			linear-gradient(180deg, #fffdf8 0%, #fff4ec 46%, #fffaf4 100%);
	}

	.profile-mask {
		position: fixed;
		inset: 0;
		z-index: 20;
		padding: 40rpx;
		background: rgba(36, 28, 24, 0.42);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.profile-dialog {
		position: relative;
		width: 100%;
		max-width: 640rpx;
		padding: 38rpx 30rpx 34rpx;
		border-radius: 36rpx;
		background: linear-gradient(180deg, #fffdf9 0%, #fff5ed 100%);
		box-shadow: 0 28rpx 56rpx rgba(71, 50, 39, 0.18);
	}

	.profile-close {
		position: absolute;
		top: 18rpx;
		right: 24rpx;
		font-size: 40rpx;
		line-height: 1;
		color: #8b7168;
	}

	.profile-title {
		display: block;
		font-size: 40rpx;
		font-weight: 700;
		color: #2f211d;
		text-align: center;
	}

	.profile-desc {
		display: block;
		margin-top: 14rpx;
		font-size: 26rpx;
		line-height: 1.6;
		color: #715d56;
		text-align: center;
	}

	.profile-avatar-wrap {
		display: flex;
		justify-content: center;
		margin-top: 30rpx;
	}

	.profile-avatar-trigger {
		padding: 0;
		background: transparent;
		border: none;
		line-height: 1;
	}

	.profile-avatar-trigger::after {
		border: none;
	}

	.profile-avatar {
		width: 164rpx;
		height: 164rpx;
		border-radius: 50%;
		background: #f5e7db;
	}

	.profile-avatar-empty {
		display: flex;
		align-items: center;
		justify-content: center;
		color: #9c7a6a;
		font-size: 26rpx;
		border: 2rpx dashed rgba(156, 122, 106, 0.35);
	}

	.profile-picker-btn,
	.profile-confirm-btn {
		margin-top: 24rpx;
		height: 88rpx;
		line-height: 88rpx;
		border-radius: 999rpx;
		font-size: 28rpx;
		font-weight: 600;
		border: none;
	}

	.profile-picker-btn {
		background: rgba(255, 255, 255, 0.86);
		color: #4e3d37;
	}

	.profile-confirm-btn {
		background: linear-gradient(90deg, #2f2a47 0%, #594a83 100%);
		color: #fff9f0;
		box-shadow: 0 18rpx 32rpx rgba(77, 62, 109, 0.22);
	}

	.profile-picker-btn::after,
	.profile-confirm-btn::after {
		border: none;
	}

	.profile-input-shell {
		margin-top: 22rpx;
		padding: 0 28rpx;
		height: 94rpx;
		border-radius: 999rpx;
		border: 2rpx solid rgba(94, 68, 54, 0.1);
		background: rgba(255, 255, 255, 0.92);
		display: flex;
		align-items: center;
	}

	.profile-input {
		width: 100%;
		font-size: 28rpx;
		color: #342925;
	}

	.hero {
		position: relative;
		min-height: 100vh;
		padding: 56rpx 30rpx 48rpx;
		overflow: hidden;
	}

	.hero-backdrop {
		position: absolute;
		border-radius: 50%;
		filter: blur(10rpx);
		opacity: 0.55;
	}

	.hero-backdrop-left {
		width: 320rpx;
		height: 320rpx;
		left: -120rpx;
		top: -30rpx;
		background: linear-gradient(180deg, #ffd5bc 0%, #ffb58b 100%);
	}

	.hero-backdrop-right {
		width: 280rpx;
		height: 280rpx;
		right: -90rpx;
		top: 220rpx;
		background: linear-gradient(180deg, #cbe8ff 0%, #8ec8ff 100%);
	}

	.hero-copy,
	.form-card {
		position: relative;
		z-index: 2;
	}

	.eyebrow {
		display: block;
		font-size: 24rpx;
		letter-spacing: 6rpx;
		color: #8d5d41;
		margin-bottom: 16rpx;
	}

	.headline {
		display: block;
		font-size: 64rpx;
		line-height: 1.18;
		font-weight: 700;
		color: #2f211d;
	}

	.subhead {
		display: block;
		margin-top: 22rpx;
		font-size: 28rpx;
		line-height: 1.7;
		color: #6d5b56;
	}

	.form-card {
		margin-top: 42rpx;
		padding: 34rpx 28rpx;
		border-radius: 36rpx;
		background: rgba(255, 255, 255, 0.78);
		box-shadow: 0 20rpx 44rpx rgba(117, 88, 63, 0.1);
		backdrop-filter: blur(10rpx);
	}

	.field-block {
		position: relative;
		margin-bottom: 28rpx;
	}

	.field-label {
		display: block;
		margin-bottom: 14rpx;
		font-size: 28rpx;
		font-weight: 600;
		color: #3f2d26;
	}

	.input-shell {
		padding: 0 28rpx;
		height: 94rpx;
		border-radius: 999rpx;
		border: 2rpx solid rgba(94, 68, 54, 0.1);
		background: rgba(255, 255, 255, 0.86);
		display: flex;
		align-items: center;
		box-sizing: border-box;
	}

	.input-shell.active {
		border-color: rgba(89, 74, 131, 0.28);
		box-shadow: 0 12rpx 28rpx rgba(89, 74, 131, 0.1);
	}

	.text-input {
		width: 100%;
		font-size: 28rpx;
		color: #342925;
	}

	.options-panel {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		z-index: 12;
		margin-top: 16rpx;
		padding: 10rpx;
		border-radius: 28rpx;
		background: rgba(255, 255, 255, 0.96);
		box-shadow: 0 18rpx 32rpx rgba(87, 58, 37, 0.1);
	}

	.option-item {
		padding: 20rpx 22rpx;
		border-radius: 20rpx;
		font-size: 28rpx;
		color: #4e3d37;
	}

	.option-item + .option-item {
		margin-top: 8rpx;
	}

	.empty-tip {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		z-index: 12;
		display: block;
		margin-top: 16rpx;
		padding: 18rpx 8rpx 0;
		font-size: 24rpx;
		color: #9c7a6a;
	}

	.action-row {
		display: flex;
		gap: 16rpx;
		margin-top: 26rpx;
		min-height: 120rpx;
		align-items: stretch;
	}

	.action-row-stacked {
		flex-direction: column;
	}

	.action-btn {
		flex: 1;
		min-height: 80rpx;
		padding: 0 24rpx;
		border-radius: 999rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		box-sizing: border-box;
	}

	.action-btn text {
		font-size: 34rpx;
		font-weight: 600;
		line-height: 1;
	}

	.primary-btn {
		background: linear-gradient(90deg, #2f2a47 0%, #594a83 100%);
		color: #fff9f0;
		box-shadow: 0 18rpx 32rpx rgba(77, 62, 109, 0.22);
	}

	.ghost-btn {
		background: rgba(255, 255, 255, 0.68);
		color: #4e3d37;
		border: 2rpx solid rgba(94, 68, 54, 0.12);
	}

	@media screen and (max-width: 420px) {
		.headline {
			font-size: 56rpx;
		}

		.action-row {
			flex-direction: column;
		}
	}
</style>
