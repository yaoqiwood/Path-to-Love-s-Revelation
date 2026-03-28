<template>
	<view class="page">
		<view class="page-glow page-glow-left"></view>
		<view class="page-glow page-glow-right"></view>
		<view class="top-bar">
			<view class="top-copy">
				<text class="top-title">消息</text>
				<view class="top-subtitle-row">
					<text class="top-subtitle">今天也适合说句悄悄话</text>
					<text class="top-heart">♡</text>
				</view>
			</view>
			<view class="top-badge">
				<text
					>剩余心动值
					{{ selfProfile.remaining_heart_value ?? selfProfile.heart_message_quota ?? 0 }}</text
				>
			</view>
		</view>

		<view class="wechat-shell">
			<view v-if="activeTab === 'contacts'" class="search-bar">
				<view class="search-box">
					<text class="search-icon">搜</text>
					<input
						v-model.trim="keyword"
						class="search-input"
						placeholder="搜索昵称或姓名"
						confirm-type="search"
						@confirm="handleSearch"
					/>
				</view>
				<text v-if="keyword" class="search-reset" @click="resetKeyword">清空</text>
			</view>

			<view v-if="activeTab === 'contacts'" class="panel contacts-panel">
				<view class="panel-head">
					<text class="panel-title">联系人</text>
					<text class="panel-tip">遇见 {{ contacts.length }} 位心动对象</text>
				</view>

				<view v-if="loading" class="empty-box">
					<text>正在加载联系人...</text>
				</view>
				<view v-else-if="!contacts.length" class="empty-box">
					<text>暂时还没有可聊天的人</text>
				</view>
				<scroll-view v-else scroll-y class="contact-scroll">
					<view class="contact-list">
						<view
							v-for="item in contacts"
							:key="item._id"
							class="contact-item"
							:class="activeContact && activeContact._id === item._id ? 'contact-item active' : ''"
							@click="selectContact(item)"
						>
							<view class="avatar-shell">
								<image
									v-if="item.personal_photo"
									class="avatar"
									:src="item.personal_photo"
									mode="aspectFill"
								></image>
								<view v-else class="avatar avatar-fallback">{{
									getAvatarText(item.nickname || item.name)
								}}</view>
							</view>
							<view class="contact-main">
								<view class="contact-top">
									<view class="contact-name-row">
										<text class="contact-name">{{
											item.nickname || item.name || '未命名联系人'
										}}</text>
										<text
											v-if="getGenderBadge(item.gender)"
											class="gender-badge"
											:class="getGenderBadge(item.gender).className"
										>
											{{ getGenderBadge(item.gender).symbol }}
										</text>
									</view>
									<text class="contact-time">{{ formatTime(item.latest_message_at) }}</text>
								</view>
								<text class="contact-meta">{{ item.name || '暂未填写姓名' }}</text>
								<view class="contact-preview-row">
									<text class="contact-preview">{{
										item.latest_message || '还没有消息，快去打个招呼吧'
									}}</text>
								</view>
								<text v-if="item.can_send === false" class="turn-tip"
									>等待对方回复后才能继续发送</text
								>
							</view>
							<view
								v-if="activeContact && activeContact._id === item._id"
								class="contact-active-dot"
							></view>
						</view>
					</view>
				</scroll-view>
			</view>

			<view v-if="activeTab === 'inbox'" class="panel contacts-panel">
				<view class="panel-head">
					<text class="panel-title">收信箱</text>
					<text class="panel-tip">陌生人来信 {{ inboxList.length }} 封</text>
				</view>
				<view v-if="inboxLoading" class="empty-box">
					<text>正在加载收信箱...</text>
				</view>
				<view v-else-if="!inboxList.length" class="empty-box">
					<text>暂时没有陌生人来信</text>
				</view>
				<scroll-view v-else scroll-y class="contact-scroll">
					<view class="contact-list">
						<view v-for="item in inboxList" :key="item.message_id" class="contact-item">
							<view class="avatar-shell">
								<view class="avatar avatar-fallback">匿</view>
							</view>
							<view class="contact-main">
								<view class="contact-top">
									<view class="contact-name-row">
										<text class="contact-name">陌生人来信</text>
										<text class="preview-tag normal-tag"> {{ item.sender_mbti || '-' }}</text>
									</view>
									<text class="contact-time">{{ formatTime(item.created_at) }}</text>
								</view>
								<view class="contact-preview-row">
									<text class="contact-preview">{{ item.content || '-' }}</text>
								</view>
							</view>
							<button class="mini-reply-btn" @click="openInboxReply(item)">回复</button>
						</view>
					</view>
				</scroll-view>
			</view>
		</view>

		<view v-if="showChatPopup && activeContact" class="chat-popup-mask" @click="closeChatPopup">
			<view class="chat-popup" @click.stop>
				<view class="chat-head">
					<view class="chat-user">
						<view class="avatar-shell small">
							<image
								v-if="activeContact.personal_photo"
								class="avatar"
								:src="activeContact.personal_photo"
								mode="aspectFill"
							></image>
							<view v-else class="avatar avatar-fallback">{{
								getAvatarText(activeContact.nickname || activeContact.name)
							}}</view>
						</view>
						<view class="chat-user-text">
							<text class="chat-name">{{ activeContact.nickname || activeContact.name }}</text>
							<text class="chat-meta">{{ activeContact.name || '未填写姓名' }}</text>
							<text class="chat-mood">和 Ta 的聊天，也许会有一点点心动</text>
						</view>
					</view>
					<view class="chat-head-actions">
						<view class="quota-badge">
							<!-- <text>{{ selfProfile.heart_message_quota || 0 }} 点</text> -->
						</view>
						<text class="chat-close" @click="closeChatPopup">×</text>
					</view>
				</view>

				<scroll-view
					scroll-y
					class="message-scroll popup-message-scroll"
					:scroll-into-view="scrollIntoView"
					scroll-with-animation
				>
					<view v-if="chatLoading && !messages.length" class="empty-box small-empty">
						<text>正在加载聊天记录...</text>
					</view>
					<view v-else-if="!messages.length" class="empty-box small-empty">
						<text>还没有聊天记录，主动说句话吧</text>
					</view>
					<view v-else class="message-list">
						<view
							v-for="item in messages"
							:id="'msg-' + item._id"
							:key="item._id"
							class="message-row"
							:class="item.sender_record_id === selfProfile._id ? 'mine' : 'other'"
						>
							<text class="bubble-time">{{
								formatDateTime(item.created_at_text || item.created_at)
							}}</text>
							<view class="bubble-wrap">
								<view class="avatar-shell mini" v-if="item.sender_record_id !== selfProfile._id">
									<image
										v-if="activeContact.personal_photo"
										class="avatar"
										:src="activeContact.personal_photo"
										mode="aspectFill"
									></image>
									<view v-else class="avatar avatar-fallback">{{
										getAvatarText(activeContact.nickname || activeContact.name)
									}}</view>
								</view>
								<view class="bubble-box">
									<view class="bubble">
										<text class="bubble-text">{{ item.content }}</text>
									</view>
								</view>
							</view>
						</view>
					</view>
				</scroll-view>

				<view class="composer">
					<textarea
						v-model.trim="draftMessage"
						class="composer-input"
						maxlength="300"
						placeholder="输入你想说的话"
					></textarea>
					<view class="composer-foot">
						<text class="composer-tip">发送后需等待对方回复，你才能继续发送下一条</text>
					</view>
					<view class="composer-actions">
						<button class="send-btn" :disabled="!canSubmitMessage" @click="sendMessage">
							发送
						</button>
					</view>
				</view>
			</view>
		</view>

		<view
			v-if="showInboxReplyPopup && activeInboxItem"
			class="chat-popup-mask"
			@click="closeInboxReplyPopup"
		>
			<view class="chat-popup" @click.stop>
				<view class="chat-head">
					<view class="chat-user-text">
						<text class="chat-name">回复陌生人来信</text>
						<text class="chat-meta"
							>仅显示发件人 MBTI：{{ activeInboxItem.sender_mbti || '-' }}</text
						>
					</view>
					<text class="chat-close" @click="closeInboxReplyPopup">×</text>
				</view>
				<view class="inbox-letter-box">
					<text class="inbox-letter-time">{{ formatDateTime(activeInboxItem.created_at) }}</text>
					<text class="inbox-letter-text">{{ activeInboxItem.content || '-' }}</text>
				</view>
				<view class="composer">
					<textarea
						v-model.trim="inboxReplyText"
						class="composer-input"
						maxlength="300"
						placeholder="输入你的回复内容"
					></textarea>
					<view class="composer-foot">
						<text class="composer-tip">回复后需要等待对方再次发送，你才能继续发下一条</text>
					</view>
					<view class="composer-actions">
						<button class="send-btn" :disabled="!canSubmitInboxReply" @click="sendInboxReply">
							回复
						</button>
					</view>
				</view>
			</view>
		</view>

		<view class="bottom-nav">
			<view
				class="bottom-tab"
				:class="activeTab === 'contacts' ? 'bottom-tab-active' : ''"
				@click="openContacts"
			>
				<text class="bottom-tab-text">联系人</text>
			</view>
			<view
				class="bottom-tab"
				:class="activeTab === 'inbox' ? 'bottom-tab-active' : ''"
				@click="openInbox"
			>
				<text class="bottom-tab-text">收信箱</text>
			</view>
		</view>
	</view>
</template>

<script>
	import { personnelUserService as personnelUser } from '@/api/modules/personnel-user'
	const PERSONNEL_PROFILE_STORAGE_KEY = 'mbtiPersonnelProfile'

	export default {
		data() {
			return {
				activeTab: 'contacts',
				loading: false,
				inboxLoading: false,
				chatLoading: false,
				sending: false,
				inboxSending: false,
				keyword: '',
				personnelId: '',
				selfProfile: {
					_id: '',
					person_id: '',
					nickname: '',
					name: '',
					mbti: '',
					personal_photo: '',
					remaining_heart_value: 3,
					heart_message_quota: 0
				},
				contacts: [],
				inboxList: [],
				activeContact: null,
				showChatPopup: false,
				showInboxReplyPopup: false,
				activeInboxItem: null,
				messages: [],
				draftMessage: '',
				inboxReplyText: '',
				canSendToActive: true,
				cannotSendReason: '',
				scrollIntoView: '',
				realtimeTimer: null,
				realtimeIdleMs: 18000,
				realtimeWaitingReplyMs: 9000,
				realtimeActiveTypingMs: 3000,
				realtimeMaxBackoffMs: 45000,
				realtimeErrorRetryMs: 5000,
				realtimeFetching: false,
				realtimeNoChangeCount: 0,
				messageStateTimer: null,
				messageStateMs: 60000,
				messageStateFetching: false,
				messageStateReady: false,
				messageState: {
					contactsVersion: 0,
					inboxVersion: 0,
					latestMessageAtText: '',
					updatedAtText: ''
				},
				pushRefreshHandler: null
			}
		},
		async onLoad() {
			if (!this.ensurePageAccess()) {
				return
			}
			this.bindPushRefresh()
			await Promise.all([this.loadHome(), this.loadInbox()])
			await this.syncMessageState({ refreshOnChange: false, silent: true })
			this.startMessageStatePolling()
		},
		async onShow() {
			if (this.showChatPopup && this.activeContact && this.activeContact._id) {
				this.startRealtime()
			}
			await this.syncMessageState({ refreshOnChange: false, silent: true })
			this.startMessageStatePolling()
		},
		onHide() {
			this.stopRealtime()
			this.stopMessageStatePolling()
		},
		onUnload() {
			this.stopRealtime()
			this.stopMessageStatePolling()
			this.unbindPushRefresh()
		},
		computed: {
			canSubmitMessage() {
				return !!(
					this.draftMessage &&
					this.draftMessage.trim() &&
					!this.sending &&
					this.canSendToActive
				)
			},
			canSubmitInboxReply() {
				return !!(this.inboxReplyText && this.inboxReplyText.trim() && !this.inboxSending)
			}
		},
		methods: {
			getStoredProfile() {
				try {
					const profile = uni.getStorageSync(PERSONNEL_PROFILE_STORAGE_KEY)
					return profile && typeof profile === 'object' ? profile : null
				} catch (error) {
					return null
				}
			},
			ensurePageAccess() {
				const profile = this.getStoredProfile()
				const userRole = Number(profile && profile.user_role) || 0
				if (!profile || !(profile.personnel_id || profile.id)) {
					uni.reLaunch({ url: '/pages/mbti-home/home' })
					return false
				}
				if (userRole !== 0) {
					uni.reLaunch({ url: '/pkg/guide/hub' })
					return false
				}
				this.personnelId = profile.personnel_id || profile.id || ''
				return !!this.personnelId
			},
			getDefaultMessageState() {
				return {
					contactsVersion: 0,
					inboxVersion: 0,
					latestMessageAtText: '',
					updatedAtText: ''
				}
			},
			normalizeMessageState(state = {}) {
				return {
					contactsVersion: Number(state.contacts_version) || 0,
					inboxVersion: Number(state.inbox_version) || 0,
					latestMessageAtText: state.latest_message_at_text || '',
					updatedAtText: state.updated_at_text || ''
				}
			},
			async loadHome() {
				if (!personnelUser || !this.personnelId) {
					return
				}
				this.loading = true
				try {
					const res = await personnelUser.getUserHeartMessageHome({
						personnelId: this.personnelId,
						keyword: this.keyword
					})
					this.selfProfile = Object.assign({}, this.selfProfile, res && res.self ? res.self : {})
					this.contacts = Array.isArray(res && res.contacts) ? res.contacts : []
					if (!this.contacts.length) {
						this.showChatPopup = false
						this.activeContact = null
						this.messages = []
						this.stopRealtime()
						return
					}
					if (this.activeContact && this.activeContact._id) {
						const nextActive = this.contacts.find((item) => item._id === this.activeContact._id)
						if (nextActive) {
							this.activeContact = Object.assign({}, this.activeContact, nextActive)
						} else {
							this.showChatPopup = false
							this.activeContact = null
							this.messages = []
							this.stopRealtime()
						}
					}
				} catch (error) {
					uni.showToast({
						title: (error && error.message) || '加载失败',
						icon: 'none'
					})
				} finally {
					this.loading = false
				}
			},
			async loadInbox(options = {}) {
				if (!personnelUser || !this.personnelId) {
					return
				}
				const silent = !!(options && options.silent)
				const previousInboxSize = Array.isArray(this.inboxList) ? this.inboxList.length : 0
				if (!silent) {
					this.inboxLoading = true
				}
				try {
					const res = await personnelUser.listUserInboxLetters({
						personnelId: this.personnelId,
						keyword: this.keyword
					})
					this.selfProfile = Object.assign({}, this.selfProfile, res && res.self ? res.self : {})
					this.inboxList = Array.isArray(res && res.list) ? res.list : []
					if (silent) {
						const nextInboxSize = this.inboxList.length
						if (nextInboxSize !== previousInboxSize) {
							console.log('[heart-message][polling][inbox]', {
								personnelId: this.personnelId,
								previousInboxSize,
								nextInboxSize,
								updatedAt: new Date().toISOString()
							})
						}
					}
				} catch (error) {
					if (!silent) {
						uni.showToast({
							title: (error && error.message) || '收信箱加载失败',
							icon: 'none'
						})
					}
				} finally {
					if (!silent) {
						this.inboxLoading = false
					}
				}
			},
			async syncMessageState(options = {}) {
				if (!personnelUser || !this.personnelId || this.messageStateFetching) {
					return false
				}
				const refreshOnChange = !!(options && options.refreshOnChange)
				const silent = !!(options && options.silent)
				this.messageStateFetching = true
				try {
					const res = await personnelUser.getUserHeartMessageState({
						personnelId: this.personnelId
					})
					this.selfProfile = Object.assign({}, this.selfProfile, res && res.self ? res.self : {})
					const nextState = this.normalizeMessageState(res && res.state ? res.state : {})
					const previousState = this.messageStateReady
						? this.messageState
						: this.getDefaultMessageState()
					const hasContactsChanged =
						this.messageStateReady && nextState.contactsVersion !== previousState.contactsVersion
					const hasInboxChanged =
						this.messageStateReady && nextState.inboxVersion !== previousState.inboxVersion
					this.messageState = nextState
					this.messageStateReady = true
					if (refreshOnChange && (hasContactsChanged || hasInboxChanged)) {
						console.log('[heart-message][state-change]', {
							personnelId: this.personnelId,
							previousState,
							nextState,
							checkedAt: new Date().toISOString()
						})
						await Promise.all([
							this.loadHome(),
							this.loadInbox({ silent: this.activeTab !== 'inbox' })
						])
					}
					return hasContactsChanged || hasInboxChanged
				} catch (error) {
					if (!silent) {
						console.error('syncMessageState failed', error)
					}
					return false
				} finally {
					this.messageStateFetching = false
				}
			},
			bindPushRefresh() {
				if (!uni.onPushMessage || this.pushRefreshHandler) {
					return
				}
				this.pushRefreshHandler = (res) => {
					this.handlePushRefresh(res)
				}
				uni.onPushMessage(this.pushRefreshHandler)
			},
			unbindPushRefresh() {
				if (!uni.offPushMessage || !this.pushRefreshHandler) {
					this.pushRefreshHandler = null
					return
				}
				uni.offPushMessage(this.pushRefreshHandler)
				this.pushRefreshHandler = null
			},
			async handlePushRefresh(res) {
				const rawPayload = res && (res.data || res.payload)
				let payload = rawPayload
				if (typeof rawPayload === 'string') {
					try {
						payload = JSON.parse(rawPayload)
					} catch (error) {
						payload = null
					}
				}
				if (!payload || payload.type !== 'heart-message-refresh') {
					return
				}
				if (payload.receiverPersonnelId && payload.receiverPersonnelId !== this.personnelId) {
					return
				}
				console.log('[heart-message][push]', {
					personnelId: this.personnelId,
					payload,
					receivedAt: new Date().toISOString()
				})
				await Promise.all([this.loadHome(), this.loadInbox({ silent: true })])
				await this.syncMessageState({ refreshOnChange: false, silent: true })
				if (
					this.showChatPopup &&
					this.activeContact &&
					this.activeContact._id &&
					payload.senderPersonnelId === this.activeContact._id
				) {
					await this.selectContact(this.activeContact, { silent: true })
				}
			},
			startMessageStatePolling() {
				this.stopMessageStatePolling()
				this.scheduleMessageStatePolling(this.messageStateMs)
			},
			scheduleMessageStatePolling(delayMs) {
				const nextDelay = Number(delayMs) > 0 ? Number(delayMs) : this.messageStateMs
				this.messageStateTimer = setTimeout(() => {
					this.messageStateTick()
				}, nextDelay)
			},
			stopMessageStatePolling() {
				if (this.messageStateTimer) {
					clearTimeout(this.messageStateTimer)
					this.messageStateTimer = null
				}
				this.messageStateFetching = false
			},
			async messageStateTick() {
				if (!personnelUser || !this.personnelId) {
					return
				}
				if (this.messageStateFetching || this.inboxSending || this.sending) {
					this.scheduleMessageStatePolling(this.messageStateMs)
					return
				}
				try {
					console.log('[heart-message][polling][state-check]', {
						personnelId: this.personnelId,
						intervalMs: this.messageStateMs,
						checkedAt: new Date().toISOString()
					})
					await this.syncMessageState({
						refreshOnChange: true,
						silent: true
					})
				} catch (error) {
					console.error('messageStateTick failed', error)
				}
				this.scheduleMessageStatePolling(this.messageStateMs)
			},
			startRealtime() {
				this.stopRealtime()
				this.resetRealtimeBackoff()
				this.scheduleRealtime(300)
			},
			scheduleRealtime(delayMs) {
				const nextDelay = Number(delayMs) > 0 ? Number(delayMs) : this.realtimeIdleMs
				this.realtimeTimer = setTimeout(() => {
					this.realtimeTick()
				}, nextDelay)
			},
			stopRealtime() {
				if (this.realtimeTimer) {
					clearTimeout(this.realtimeTimer)
					this.realtimeTimer = null
				}
				this.realtimeFetching = false
				this.resetRealtimeBackoff()
			},
			resetRealtimeBackoff() {
				this.realtimeNoChangeCount = 0
			},
			getRealtimeDelay(hasNewMessage) {
				if (hasNewMessage) {
					return this.realtimeActiveTypingMs
				}
				const baseDelay = !this.canSendToActive ? this.realtimeWaitingReplyMs : this.realtimeIdleMs
				const backoffLevel = Math.min(this.realtimeNoChangeCount, 3)
				return Math.min(baseDelay * Math.pow(2, backoffLevel), this.realtimeMaxBackoffMs)
			},
			mergeMessageList(incoming = []) {
				if (!Array.isArray(incoming) || !incoming.length) {
					return this.messages
				}
				const map = {}
				const merged = []
				this.messages.forEach((item) => {
					if (!item || !item._id || map[item._id]) {
						return
					}
					map[item._id] = true
					merged.push(item)
				})
				incoming.forEach((item) => {
					if (!item || !item._id || map[item._id]) {
						return
					}
					map[item._id] = true
					merged.push(item)
				})
				merged.sort(
					(left, right) =>
						new Date(left.created_at || left.created_at_text || 0).getTime() -
						new Date(right.created_at || right.created_at_text || 0).getTime()
				)
				return merged
			},
			async realtimeTick() {
				if (!personnelUser || !this.personnelId) {
					return
				}
				if (!this.showChatPopup || !this.activeContact || !this.activeContact._id) {
					return
				}
				if (this.realtimeFetching || this.chatLoading || this.sending) {
					this.scheduleRealtime(this.realtimeActiveTypingMs)
					return
				}
				this.realtimeFetching = true
				const contactId = this.activeContact._id
				let hasNewMessage = false
				try {
					const lastMessage = this.messages.length ? this.messages[this.messages.length - 1] : null
					const since = lastMessage
						? lastMessage.created_at_text || lastMessage.created_at || ''
						: ''
					const res = await personnelUser.listUserHeartMessages({
						personnelId: this.personnelId,
						contactId,
						since
					})
					if (!this.showChatPopup || !this.activeContact || this.activeContact._id !== contactId) {
						return
					}
					const incoming = Array.isArray(res && res.list) ? res.list : []
					const nextMessages = this.mergeMessageList(incoming)
					const prevLast = this.messages.length ? this.messages[this.messages.length - 1]._id : ''
					const nextLast = nextMessages.length ? nextMessages[nextMessages.length - 1]._id : ''
					hasNewMessage = !!nextLast && nextLast !== prevLast
					this.selfProfile = Object.assign({}, this.selfProfile, res && res.self ? res.self : {})
					this.activeContact = Object.assign(
						{},
						this.activeContact,
						res && res.contact ? res.contact : {}
					)
					this.messages = nextMessages
					this.canSendToActive = !!(res && res.can_send !== false)
					this.cannotSendReason = (res && res.can_send_reason) || '请等待对方回复后再发送下一条'
					this.realtimeNoChangeCount = hasNewMessage ? 0 : this.realtimeNoChangeCount + 1
					if (hasNewMessage) {
						console.log('[heart-message][polling][chat]', {
							personnelId: this.personnelId,
							contactId,
							incomingCount: incoming.length,
							latestMessageId: nextLast,
							receivedAt: new Date().toISOString()
						})
						this.$nextTick(() => {
							this.scrollIntoView = 'msg-' + nextLast
						})
					}
				} catch (error) {
					this.realtimeNoChangeCount = 0
					this.scheduleRealtime(this.realtimeErrorRetryMs)
					return
				} finally {
					this.realtimeFetching = false
				}
				this.scheduleRealtime(this.getRealtimeDelay(hasNewMessage))
			},
			async selectContact(item, options = {}) {
				if (!item || !item._id || !personnelUser) {
					return
				}
				const silent = !!(options && options.silent)
				const isSameContact =
					this.showChatPopup && this.activeContact && this.activeContact._id === item._id
				this.showChatPopup = true
				this.activeContact = item
				if (!isSameContact && !silent) {
					this.messages = []
					this.scrollIntoView = ''
				}
				this.chatLoading = !silent && (!isSameContact || !this.messages.length)
				try {
					const res = await personnelUser.listUserHeartMessages({
						personnelId: this.personnelId,
						contactId: item._id
					})
					this.selfProfile = Object.assign({}, this.selfProfile, res && res.self ? res.self : {})
					this.activeContact = Object.assign({}, item, res && res.contact ? res.contact : {})
					this.messages = Array.isArray(res && res.list) ? res.list : []
					this.canSendToActive = !!(res && res.can_send !== false)
					this.cannotSendReason = (res && res.can_send_reason) || '请等待对方回复后再发送下一条'
					this.$nextTick(() => {
						const lastMessage = this.messages[this.messages.length - 1]
						this.scrollIntoView = lastMessage ? 'msg-' + lastMessage._id : ''
					})
				} catch (error) {
					uni.showToast({
						title: (error && error.message) || '聊天记录加载失败',
						icon: 'none'
					})
				} finally {
					this.chatLoading = false
					if (this.showChatPopup && this.activeContact && this.activeContact._id) {
						this.startRealtime()
					}
				}
			},
			closeChatPopup() {
				this.showChatPopup = false
				this.stopRealtime()
			},
			resetKeyword() {
				this.keyword = ''
				if (this.activeTab === 'inbox') {
					this.loadInbox()
					return
				}
				this.loadHome()
			},
			openContacts() {
				this.activeTab = 'contacts'
				this.loadHome()
			},
			handleSearch() {
				if (this.activeTab === 'inbox') {
					this.loadInbox()
					return
				}
				this.loadHome()
			},
			openInbox() {
				this.activeTab = 'inbox'
				this.loadInbox()
				this.startMessageStatePolling()
			},
			openInboxReply(item) {
				if (!item || !item.contact_id) {
					return
				}
				if (item.can_reply === false) {
					uni.showToast({
						title: item.can_reply_reason || '请等待对方再次来信',
						icon: 'none'
					})
					return
				}
				this.activeInboxItem = item
				this.inboxReplyText = ''
				this.showInboxReplyPopup = true
			},
			closeInboxReplyPopup() {
				this.showInboxReplyPopup = false
				this.activeInboxItem = null
				this.inboxReplyText = ''
			},
			async sendInboxReply() {
				if (!this.activeInboxItem || !this.activeInboxItem.contact_id) {
					return
				}
				if (!this.inboxReplyText) {
					uni.showToast({
						title: '请输入回复内容',
						icon: 'none'
					})
					return
				}
				if (this.inboxSending) {
					return
				}
				this.inboxSending = true
				try {
					await personnelUser.sendUserHeartMessage({
						personnelId: this.personnelId,
						contactId: this.activeInboxItem.contact_id,
						content: this.inboxReplyText,
						type: 0,
						scene: 'inbox'
					})
					this.closeInboxReplyPopup()
					await Promise.all([this.loadHome(), this.loadInbox()])
					await this.syncMessageState({ refreshOnChange: false, silent: true })
					uni.showToast({
						title: '回复成功',
						icon: 'success'
					})
				} catch (error) {
					uni.showToast({
						title: (error && error.message) || '回复失败',
						icon: 'none'
					})
				} finally {
					this.inboxSending = false
				}
			},
			async sendMessage() {
				if (!this.activeContact || !this.activeContact._id) {
					return
				}
				if (!this.canSendToActive) {
					uni.showToast({
						title: this.cannotSendReason || '请等待对方回复后再发送下一条',
						icon: 'none'
					})
					return
				}
				if (!this.draftMessage) {
					uni.showToast({
						title: '请输入消息内容',
						icon: 'none'
					})
					return
				}
				if (this.sending) {
					return
				}
				this.sending = true
				try {
					await personnelUser.sendUserHeartMessage({
						personnelId: this.personnelId,
						contactId: this.activeContact._id,
						content: this.draftMessage,
						type: 0,
						scene: 'contacts'
					})
					const currentContactId = this.activeContact._id
					this.draftMessage = ''
					await Promise.all([this.loadHome(), this.loadInbox()])
					const nextActive = this.contacts.find((item) => item._id === currentContactId)
					if (nextActive) {
						await this.selectContact(nextActive, { silent: true })
					}
					await this.syncMessageState({ refreshOnChange: false, silent: true })
					uni.showToast({
						title: '发送成功',
						icon: 'success'
					})
				} catch (error) {
					uni.showToast({
						title: (error && error.message) || '发送失败',
						icon: 'none'
					})
				} finally {
					this.sending = false
				}
			},
			getAvatarText(value) {
				const text = String(value || '').trim()
				return text ? text.slice(0, 1) : '聊'
			},
			getGenderBadge(value) {
				const gender = String(value || '')
					.trim()
					.toLowerCase()
				if (
					gender === '男' ||
					gender === '1' ||
					gender === 'm' ||
					gender === 'male' ||
					gender === 'man'
				) {
					return {
						symbol: '♂',
						className: 'gender-male'
					}
				}
				if (
					gender === '女' ||
					gender === '2' ||
					gender === 'f' ||
					gender === 'female' ||
					gender === 'woman'
				) {
					return {
						symbol: '♀',
						className: 'gender-female'
					}
				}
				return null
			},
			formatTime(value) {
				if (!value) {
					return ''
				}
				const date = new Date(value)
				if (Number.isNaN(date.getTime())) {
					return ''
				}
				const now = new Date()
				const isSameDay =
					now.getFullYear() === date.getFullYear() &&
					now.getMonth() === date.getMonth() &&
					now.getDate() === date.getDate()
				if (isSameDay) {
					return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
				}
				const yesterday = new Date(now)
				yesterday.setDate(now.getDate() - 1)
				const isYesterday =
					yesterday.getFullYear() === date.getFullYear() &&
					yesterday.getMonth() === date.getMonth() &&
					yesterday.getDate() === date.getDate()
				if (isYesterday) {
					return '昨天'
				}
				return `${date.getMonth() + 1}月${date.getDate()}日`
			},
			formatDateTime(value) {
				if (!value) {
					return ''
				}
				const date = new Date(value)
				if (Number.isNaN(date.getTime())) {
					return ''
				}
				const year = date.getFullYear()
				const month = String(date.getMonth() + 1).padStart(2, '0')
				const day = String(date.getDate()).padStart(2, '0')
				const hour = String(date.getHours()).padStart(2, '0')
				const minute = String(date.getMinutes()).padStart(2, '0')
				return `${year}-${month}-${day} ${hour}:${minute}`
			}
		}
	}
</script>

<style scoped lang="less">
	.page {
		position: relative;
		height: 100vh;
		background:
			radial-gradient(circle at top left, rgba(222, 236, 224, 0.86), transparent 28%),
			radial-gradient(circle at top right, rgba(244, 230, 199, 0.76), transparent 24%),
			linear-gradient(180deg, #faf9f5 0%, #f2f0e9 38%, #eae8e0 100%);
		box-sizing: border-box;
		overflow: hidden;
		display: flex;
		flex-direction: column;
	}

	.page-glow {
		position: absolute;
		border-radius: 50%;
		filter: blur(10rpx);
		opacity: 0.8;
		pointer-events: none;
	}

	.page-glow-left {
		left: -80rpx;
		top: 140rpx;
		width: 220rpx;
		height: 220rpx;
		background: rgba(184, 214, 188, 0.62);
	}

	.page-glow-right {
		right: -60rpx;
		top: 420rpx;
		width: 180rpx;
		height: 180rpx;
		background: rgba(220, 205, 168, 0.58);
	}

	.top-bar {
		position: relative;
		z-index: 1;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 28rpx 24rpx 18rpx;
		background: linear-gradient(
			180deg,
			rgba(255, 255, 255, 0.78) 0%,
			rgba(246, 244, 236, 0.34) 100%
		);
	}

	.top-copy {
		max-width: 70%;
	}

	.top-title {
		display: block;
		font-size: 40rpx;
		font-weight: 700;
		color: #2f342d;
	}

	.top-subtitle-row {
		display: flex;
		align-items: center;
		gap: 10rpx;
	}

	.top-subtitle {
		display: block;
		margin-top: 8rpx;
		font-size: 24rpx;
		color: #72786c;
	}

	.top-heart {
		margin-top: 8rpx;
		font-size: 24rpx;
		color: #7da57f;
	}

	.top-badge {
		padding: 12rpx 20rpx;
		border-radius: 999rpx;
		background: linear-gradient(135deg, #edf4e9 0%, #f9f1dc 100%);
		font-size: 24rpx;
		color: #5f775d;
		box-shadow: 0 10rpx 24rpx rgba(127, 149, 118, 0.12);
	}

	.wechat-shell {
		position: relative;
		z-index: 1;
		flex: 1;
		display: flex;
		flex-direction: column;
		min-height: 0;
		padding: 0 0 calc(164rpx + env(safe-area-inset-bottom));
		box-sizing: border-box;
		overflow: hidden;
	}

	.search-bar {
		display: flex;
		align-items: center;
		gap: 18rpx;
		padding: 0 24rpx 20rpx;
	}

	.search-box {
		flex: 1;
		height: 72rpx;
		padding: 0 24rpx;
		border-radius: 18rpx;
		background: rgba(255, 255, 255, 0.92);
		display: flex;
		align-items: center;
		box-sizing: border-box;
		box-shadow: 0 12rpx 24rpx rgba(140, 146, 122, 0.1);
	}

	.search-icon {
		margin-right: 16rpx;
		font-size: 24rpx;
		color: #999999;
	}

	.search-input {
		flex: 1;
		height: 72rpx;
		font-size: 26rpx;
		color: #222222;
	}

	.search-reset {
		font-size: 26rpx;
		color: #6b7d63;
	}

	.panel {
		margin: 0 24rpx 24rpx;
		border-radius: 24rpx;
		overflow: hidden;
		background: rgba(255, 255, 255, 0.9);
		box-shadow: 0 18rpx 34rpx rgba(126, 128, 111, 0.1);
		backdrop-filter: blur(8rpx);
	}

	.contacts-panel {
		flex: 1;
		display: flex;
		flex-direction: column;
		min-height: 0;
	}

	.contact-scroll {
		flex: 1;
		min-height: 0;
	}

	.panel-head,
	.contact-item,
	.contact-top,
	.contact-preview-row,
	.chat-head,
	.chat-user,
	.composer-foot,
	.type-row,
	.message-row,
	.bubble-wrap {
		display: flex;
	}

	.panel-head {
		align-items: center;
		justify-content: space-between;
		padding: 24rpx;
		border-bottom: 1rpx solid #ece8dc;
	}

	.panel-title,
	.chat-name {
		font-size: 30rpx;
		font-weight: 600;
		color: #2f342d;
	}

	.panel-tip,
	.contact-meta,
	.contact-preview,
	.chat-meta,
	.composer-tip,
	.bubble-time,
	.empty-box,
	.empty-chat-tip {
		font-size: 24rpx;
		color: #7c7f73;
	}

	.contact-list {
		background: transparent;
	}

	.contact-item {
		align-items: center;
		padding: 22rpx 24rpx;
		gap: 20rpx;
		position: relative;
		transition: all 0.2s ease;
	}

	.contact-item::after {
		content: '';
		position: absolute;
		left: 140rpx;
		right: 24rpx;
		bottom: 0;
		height: 1rpx;
		background: #ece8dc;
	}

	.contact-item.active::after {
		display: none;
	}

	.contact-item.active {
		background: linear-gradient(135deg, #f4f6ef 0%, #faf7ec 100%);
	}

	.avatar-shell {
		flex-shrink: 0;
		width: 96rpx;
		height: 96rpx;
		border-radius: 20rpx;
		overflow: hidden;
		background: linear-gradient(180deg, #dcebd8 0%, #efe2bb 100%);
		box-shadow: 0 10rpx 20rpx rgba(150, 162, 129, 0.16);
	}

	.avatar-shell.small {
		width: 76rpx;
		height: 76rpx;
		border-radius: 18rpx;
	}

	.avatar-shell.mini {
		width: 64rpx;
		height: 64rpx;
		border-radius: 16rpx;
	}

	.avatar {
		width: 100%;
		height: 100%;
	}

	.avatar-fallback {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 100%;
		height: 100%;
		background: linear-gradient(180deg, #88b97a 0%, #d8bc73 100%);
		color: #ffffff;
		font-size: 32rpx;
		font-weight: 700;
	}

	.contact-main {
		flex: 1;
		min-width: 0;
	}

	.contact-top {
		align-items: center;
		justify-content: space-between;
		gap: 16rpx;
	}

	.contact-name-row {
		display: flex;
		align-items: center;
		gap: 10rpx;
		min-width: 0;
	}

	.contact-name {
		font-size: 30rpx;
		color: #33392f;
	}

	.gender-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-width: 40rpx;
		height: 40rpx;
		padding: 0 10rpx;
		border-radius: 999rpx;
		font-size: 22rpx;
		font-weight: 700;
		color: #ffffff;
		line-height: 1;
		flex-shrink: 0;
	}

	.gender-male {
		background: linear-gradient(135deg, #63a8ff 0%, #3f7df2 100%);
		box-shadow: 0 8rpx 16rpx rgba(80, 139, 255, 0.2);
	}

	.gender-female {
		background: linear-gradient(135deg, #ff92b2 0%, #ff6f9a 100%);
		box-shadow: 0 8rpx 16rpx rgba(255, 127, 164, 0.2);
	}

	.contact-time {
		font-size: 22rpx;
		color: #999999;
	}

	.contact-meta {
		display: block;
		margin-top: 6rpx;
	}

	.turn-tip {
		display: block;
		margin-top: 8rpx;
		font-size: 22rpx;
		color: #b1762d;
	}

	.contact-preview-row {
		align-items: center;
		gap: 12rpx;
		margin-top: 10rpx;
	}

	.preview-tag,
	.bubble-type {
		flex-shrink: 0;
		padding: 4rpx 14rpx;
		border-radius: 999rpx;
		font-size: 20rpx;
	}

	.normal-tag {
		background: #eef1ea;
		color: #6c7568;
	}

	.heart-tag {
		background: linear-gradient(135deg, #e8f2e3 0%, #f6ebcf 100%);
		color: #8a6a3f;
	}

	.contact-preview {
		flex: 1;
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.contact-active-dot {
		width: 16rpx;
		height: 16rpx;
		border-radius: 50%;
		background: #7cab79;
		box-shadow: 0 0 0 8rpx rgba(124, 171, 121, 0.12);
	}

	.mini-reply-btn {
		height: 56rpx;
		line-height: 56rpx;
		padding: 0 20rpx;
		margin: 0;
		border-radius: 12rpx;
		font-size: 24rpx;
		color: #ffffff;
		background: linear-gradient(135deg, #7ea870 0%, #cdaa61 100%);
	}

	.chat-panel {
		background: linear-gradient(
			180deg,
			rgba(249, 248, 242, 0.96) 0%,
			rgba(244, 241, 233, 0.96) 100%
		);
	}

	.chat-popup-mask {
		position: fixed;
		left: 0;
		top: 0;
		right: 0;
		bottom: 0;
		z-index: 40;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: calc(24rpx + env(safe-area-inset-top)) 24rpx calc(24rpx + env(safe-area-inset-bottom));
		background: rgba(38, 42, 34, 0.38);
		box-sizing: border-box;
	}

	.chat-popup {
		width: 100%;
		height: calc(100vh - (48rpx + env(safe-area-inset-top) + env(safe-area-inset-bottom)));
		max-height: calc(100vh - (48rpx + env(safe-area-inset-top) + env(safe-area-inset-bottom)));
		display: flex;
		flex-direction: column;
		min-height: 0;
		border-radius: 28rpx;
		overflow: hidden;
		background: linear-gradient(
			180deg,
			rgba(249, 248, 242, 0.98) 0%,
			rgba(244, 241, 233, 0.98) 100%
		);
		box-shadow: 0 24rpx 56rpx rgba(56, 63, 51, 0.2);
	}

	.chat-head {
		align-items: center;
		justify-content: space-between;
		padding: 22rpx 24rpx;
		background: linear-gradient(135deg, #f8faf3 0%, #f7f1e2 100%);
		border-bottom: 1rpx solid #e8e3d5;
	}

	.chat-head-actions {
		display: flex;
		align-items: center;
		gap: 16rpx;
		margin-left: 16rpx;
	}

	.chat-close {
		width: 52rpx;
		height: 52rpx;
		line-height: 48rpx;
		border-radius: 50%;
		text-align: center;
		font-size: 36rpx;
		color: #6a7262;
		background: rgba(255, 255, 255, 0.72);
	}

	.chat-user {
		align-items: center;
		gap: 18rpx;
		flex: 1;
		min-width: 0;
	}

	.chat-user-text {
		flex: 1;
		min-width: 0;
	}

	.chat-name,
	.chat-meta {
		display: block;
	}

	.chat-mood {
		display: block;
		margin-top: 6rpx;
		font-size: 22rpx;
		color: #87907d;
	}

	.message-scroll {
		flex: 1;
		height: auto;
		min-height: 0;
		padding: 24rpx 24rpx 8rpx;
		box-sizing: border-box;
	}

	.popup-message-scroll {
		flex: 1;
		height: auto;
		min-height: 220rpx;
		max-height: none;
	}

	.message-list {
		display: flex;
		flex-direction: column;
		gap: 22rpx;
	}

	.message-row {
		flex-direction: column;
	}

	.message-row.other {
		align-items: flex-start;
	}

	.message-row.mine {
		align-items: flex-end;
	}

	.bubble-wrap {
		align-items: flex-start;
		gap: 14rpx;
		margin-top: 8rpx;
	}

	.message-row.mine .bubble-wrap {
		justify-content: flex-end;
	}

	.message-row.mine .bubble-wrap {
		flex-direction: row-reverse;
	}

	.bubble-box {
		display: flex;
		max-width: 78%;
		min-width: 0;
	}

	.message-row.mine .bubble-box {
		flex-direction: column;
		align-items: flex-end;
	}

	.message-row.mine .bubble-time {
		text-align: right;
	}

	.message-row.mine .bubble-box,
	.message-row.mine .bubble {
		max-width: 100%;
	}

	.message-row.mine .bubble {
		background: linear-gradient(135deg, #d8e9cf 0%, #efe0ad 100%);
	}

	.bubble {
		position: relative;
		padding: 20rpx 22rpx;
		border-radius: 14rpx;
		background: #ffffff;
		box-shadow: 0 8rpx 18rpx rgba(139, 141, 121, 0.1);
	}

	.message-row.other .bubble::before {
		content: '';
		position: absolute;
		left: -10rpx;
		top: 22rpx;
		width: 20rpx;
		height: 20rpx;
		background: #ffffff;
		transform: rotate(45deg);
		border-radius: 4rpx;
	}

	.message-row.mine .bubble::before {
		content: '';
		position: absolute;
		right: -10rpx;
		top: 22rpx;
		width: 20rpx;
		height: 20rpx;
		background: #e8d59d;
		transform: rotate(45deg);
		border-radius: 4rpx;
	}

	.bubble-text {
		display: block;
		font-size: 28rpx;
		line-height: 1.6;
		color: #353a30;
		word-break: break-word;
		white-space: pre-wrap;
	}

	.composer {
		flex-shrink: 0;
		padding: 14rpx 24rpx calc(10rpx + env(safe-area-inset-bottom));
		background: linear-gradient(180deg, #faf9f4 0%, #f5f1e7 100%);
		border-top: 1rpx solid #e8e2d4;
	}

	.type-row {
		gap: 14rpx;
	}

	.type-chip {
		padding: 12rpx 24rpx;
		border-radius: 999rpx;
		background: rgba(255, 255, 255, 0.95);
		font-size: 24rpx;
		color: #6d7569;
		box-shadow: 0 8rpx 16rpx rgba(152, 153, 129, 0.08);
	}

	.type-chip.active {
		background: linear-gradient(135deg, #8ab47e 0%, #d8ba73 100%);
		color: #ffffff;
	}

	.type-chip.active.heart-chip {
		background: linear-gradient(135deg, #7da66f 0%, #c9a75d 100%);
	}

	.composer-input {
		width: 100%;
		height: 96rpx;
		min-height: 96rpx;
		margin-top: 12rpx;
		padding: 14rpx 20rpx;
		border-radius: 18rpx;
		background: rgba(255, 255, 255, 0.94);
		box-sizing: border-box;
		font-size: 28rpx;
		line-height: 1.5;
		color: #222222;
		box-shadow: inset 0 0 0 1rpx #e6e1d5;
	}

	.composer-foot {
		align-items: center;
		justify-content: flex-start;
		gap: 18rpx;
		margin-top: 16rpx;
	}

	.composer-actions {
		display: flex;
		justify-content: stretch;
		margin-top: 14rpx;
	}

	.composer-tip {
		flex: 1;
		line-height: 1.5;
	}

	.send-btn {
		width: 100%;
		height: 72rpx;
		line-height: 72rpx;
		margin: 0;
		border-radius: 14rpx;
		background: linear-gradient(135deg, #7ea870 0%, #cdaa61 100%);
		color: #ffffff;
		font-size: 28rpx;
		box-shadow: 0 12rpx 22rpx rgba(126, 150, 103, 0.2);
	}

	.send-btn[disabled] {
		background: linear-gradient(135deg, #cfd7ca 0%, #ddd6c5 100%);
		color: #f8f7f3;
		box-shadow: none;
		opacity: 1;
	}

	.inbox-letter-box {
		margin: 20rpx 24rpx 0;
		padding: 20rpx;
		border-radius: 16rpx;
		background: rgba(255, 255, 255, 0.9);
		box-shadow: inset 0 0 0 1rpx #e6e1d5;
	}

	.inbox-letter-time {
		display: block;
		font-size: 22rpx;
		color: #8d8f83;
	}

	.inbox-letter-text {
		display: block;
		margin-top: 10rpx;
		font-size: 26rpx;
		line-height: 1.6;
		color: #353a30;
	}

	.quota-badge {
		padding: 10rpx 18rpx;
		border-radius: 999rpx;
		background: linear-gradient(135deg, #edf4e9 0%, #f7edd7 100%);
		font-size: 22rpx;
		color: #61795d;
	}

	.empty-box,
	.empty-chat-panel {
		padding: 56rpx 24rpx;
		text-align: center;
	}

	.small-empty {
		padding-top: 140rpx;
	}

	.empty-chat-title {
		display: block;
		font-size: 30rpx;
		font-weight: 600;
		color: #41463c;
	}

	.empty-chat-tip {
		display: block;
		margin-top: 12rpx;
	}

	.bottom-nav {
		position: fixed;
		left: 24rpx;
		right: 24rpx;
		bottom: calc(20rpx + env(safe-area-inset-bottom));
		z-index: 20;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 20rpx;
		padding: 16rpx;
		border-radius: 28rpx;
		background: rgba(255, 255, 255, 0.92);
		box-shadow: 0 16rpx 30rpx rgba(126, 128, 111, 0.14);
		backdrop-filter: blur(12rpx);
	}

	.bottom-tab {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		height: 84rpx;
		border-radius: 22rpx;
		color: #6b7265;
		background: #f5f4ee;
	}

	.bottom-tab-active {
		background: linear-gradient(135deg, #e7f0e0 0%, #f2ead0 100%);
		color: #4f654a;
	}

	.bottom-tab-text {
		font-size: 26rpx;
		font-weight: 600;
	}

	@media screen and (max-width: 420px) {
		.top-bar,
		.search-bar {
			padding-left: 20rpx;
			padding-right: 20rpx;
		}

		.panel {
			margin-left: 20rpx;
			margin-right: 20rpx;
		}

		.composer-foot {
			align-items: flex-start;
			flex-direction: column;
		}

		.send-btn {
			width: 100%;
		}

		.bottom-nav {
			left: 20rpx;
			right: 20rpx;
		}

		.chat-popup-mask {
			padding-left: 20rpx;
			padding-right: 20rpx;
		}
	}
</style>
