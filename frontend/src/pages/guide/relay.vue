<template>
	<view class="page">
		<view class="toolbar">
			<button class="ghost-btn" @click="goBack">返回上一页</button>
			<button class="solid-btn" @click="loadAll">刷新数据</button>
		</view>

		<view class="hero-card">
			<view class="card-head">
				<text class="card-title">心动私信管理表</text>
				<text class="card-tip">
					用户可为参与者分配私信次数，并创建匿名心动私信记录。当前版本默认由用户录入发送关系，被发送者不会看到发送者身份。
				</text>
			</view>
			<view class="stats-wrap">
				<view class="stat-card">
					<text class="stat-label">私信总数</text>
					<text class="stat-value">{{ stats.total }}</text>
				</view>
				<view class="stat-card">
					<text class="stat-label">待投递</text>
					<text class="stat-value">{{ stats.queued }}</text>
				</view>
				<view class="stat-card">
					<text class="stat-label">已投递</text>
					<text class="stat-value">{{ stats.delivered }}</text>
				</view>
				<view class="stat-card">
					<text class="stat-label">草稿/撤销</text>
					<text class="stat-value">{{ stats.draft + stats.revoked }}</text>
				</view>
			</view>
		</view>

		<view class="panel-card">
			<view class="card-head">
				<text class="card-title">私信次数分配</text>
				<text class="card-tip">先搜索参与者，再为其直接设置、增加或扣减可发送次数。</text>
			</view>
			<view class="action-row quota-entry-row">
				<button class="solid-btn" @click="toggleQuotaPanel">
					{{ showQuotaPanel ? '收起次数分配' : '打开次数分配' }}
				</button>
			</view>
			<view v-if="showQuotaPanel" class="quota-panel">
				<input
					v-model.trim="candidateKeyword"
					class="search-input"
					placeholder="搜索编号 / 昵称 / 姓名 / 手机 / MBTI"
					confirm-type="search"
					@confirm="loadCandidates"
				/>
				<view v-if="candidateLoading" class="empty-box">
					<text>正在加载参与者...</text>
				</view>
				<view v-else-if="!candidateList.length" class="empty-box">
					<text>暂无可分配私信次数的参与者</text>
				</view>
					<view v-else class="candidate-list">
					<view v-for="item in candidateList" :key="item._id" class="candidate-item">
						<view class="candidate-top">
							<view class="candidate-main">
								<text class="candidate-name">{{ item.label }}</text>
								<text class="candidate-meta">
									手机号 {{ item.mobile || '-' }} | 当前可发次数 {{ item.private_message_quota || 0 }}
								</text>
							</view>
						</view>
						<view class="candidate-bottom">
							<view class="candidate-bottom-spacer"></view>
							<view class="candidate-actions">
								<input
									v-model="quotaInputs[item._id]"
									class="mini-input"
									type="number"
									placeholder="次数"
								/>
								<button class="mini-btn" @click="changeQuota(item, 'set')">设置</button>
								<button class="mini-btn" @click="changeQuota(item, 'increase')">增加</button>
								<button class="mini-btn danger-btn" @click="changeQuota(item, 'decrease')">扣减</button>
							</view>
						</view>
					</view>
					<view
						v-if="candidatePagination.total > candidatePagination.pageSize"
						class="candidate-pager"
					>
						<button
							class="pager-btn"
							:class="isCandidateFirstPage ? 'pager-btn is-disabled' : ''"
							@click="goCandidatePrevPage"
						>
							上一页
						</button>
						<text class="pager-text">
							第 {{ candidatePagination.page }} / {{ candidateTotalPages }} 页
						</text>
						<button
							class="pager-btn"
							:class="isCandidateLastPage ? 'pager-btn is-disabled' : ''"
							@click="goCandidateNextPage"
						>
							下一页
						</button>
					</view>
				</view>
			</view>
		</view>

		<view class="panel-card">
			<view class="card-head">
				<text class="card-title">私信记录</text>
				<text class="card-tip">支持筛选状态、搜索内容与双方信息，并手动新增或编辑私信记录。</text>
			</view>
			<scroll-view class="status-scroll" scroll-x>
				<view class="status-row">
					<view
						v-for="item in statusFilters"
						:key="item.value"
						class="status-chip"
						:class="messageStatus === item.value ? 'status-chip active' : 'status-chip'"
						@click="changeStatus(item.value)"
					>
						{{ item.label }}
					</view>
				</view>
			</scroll-view>
			<input
				v-model.trim="messageKeyword"
				class="search-input"
				placeholder="搜索发送方 / 接收方 / 内容 / 备注"
				confirm-type="search"
				@confirm="searchMessages"
			/>
			<view class="action-row space-between">
				<!-- <button class="solid-btn" @click="openCreate">新增私信</button> -->
				<view class="inline-actions">
					<button class="light-btn" @click="resetFilters">重置</button>
					<button class="solid-btn" @click="searchMessages">查询</button>
				</view>
			</view>

			<view v-if="showForm" class="form-panel">
				<view class="candidate-head">
					<text class="section-title">{{ currentId ? '编辑私信' : '新增私信' }}</text>
					<button class="ghost-btn mini-ghost-btn" @click="closeForm">收起</button>
				</view>
				<view class="form-grid">
					<view class="field">
						<text class="label">发送方</text>
						<picker :range="candidateLabels" :value="senderIndex" @change="onSenderChange">
							<view class="picker">{{ form.sender_record_id ? selectedSenderLabel : '请选择发送方' }}</view>
						</picker>
					</view>
					<view class="field">
						<text class="label">接收方</text>
						<picker :range="candidateLabels" :value="receiverIndex" @change="onReceiverChange">
							<view class="picker">{{ form.receiver_record_id ? selectedReceiverLabel : '请选择接收方' }}</view>
						</picker>
					</view>
					<view class="field">
						<text class="label">状态</text>
						<picker :range="statusOptionLabels" :value="statusIndex" @change="onStatusChange">
							<view class="picker">{{ statusText(form.status) }}</view>
						</picker>
					</view>
					<view class="field">
						<text class="label">消耗次数</text>
						<input v-model="form.quota_cost" class="input" type="number" placeholder="默认 1" />
					</view>
					<view class="field field-full switch-field">
						<text class="label switch-label">匿名发送</text>
						<switch :checked="form.is_anonymous" color="#1f6b52" @change="onAnonymousChange" />
					</view>
					<view class="field field-full">
						<text class="label">私信内容</text>
						<textarea
							v-model.trim="form.content"
							class="textarea"
							maxlength="300"
							placeholder="请输入这条心动私信的内容"
						></textarea>
					</view>
					<view class="field field-full">
						<text class="label">用户备注</text>
						<textarea
							v-model.trim="form.user_remark"
							class="textarea"
							maxlength="200"
							placeholder="可填写来源、投递说明、保留意见等"
						></textarea>
					</view>
				</view>
				<view class="action-row">
					<button class="ghost-btn" @click="resetForm">清空</button>
					<button class="solid-btn" @click="submitForm">{{ currentId ? '保存修改' : '创建私信' }}</button>
				</view>
			</view>

			<scroll-view scroll-x class="table-scroll">
				<view class="table">
					<view class="table-row table-header">
						<text class="col col-status">状态</text>
						<text class="col col-sender">发送方</text>
						<text class="col col-receiver">接收方</text>
						<text class="col col-content">私信内容</text>
						<text class="col col-quota">消耗次数</text>
						<text class="col col-time">创建时间</text>
						<text class="col col-action">操作</text>
					</view>
					<view v-if="loading" class="empty-box">
						<text>正在加载私信记录...</text>
					</view>
					<view v-else-if="!records.length" class="empty-box">
						<text>暂无私信记录</text>
					</view>
					<view v-for="item in records" :key="item._id" class="table-row body-row">
						<view class="col col-status">
							<text :class="'status-pill status-' + item.status">{{ statusText(item.status) }}</text>
						</view>
						<view class="col col-sender name-cell">
							<text class="primary-text">#{{ item.sender_person_id }} {{ item.sender_nickname || item.sender_name || '-' }}</text>
							<text class="secondary-text">{{ item.sender_name || '-' }} / {{ item.sender_mbti || '-' }}</text>
						</view>
						<view class="col col-receiver name-cell">
							<text class="primary-text">#{{ item.receiver_person_id }} {{ item.receiver_nickname || item.receiver_name || '-' }}</text>
							<text class="secondary-text">{{ item.receiver_name || '-' }} / {{ item.receiver_mbti || '-' }}</text>
						</view>
						<view class="col col-content content-cell">
							<text class="content-text">{{ item.content || '-' }}</text>
							<text class="secondary-text">{{ item.user_remark || '无备注' }}</text>
						</view>
						<text class="col col-quota">{{ item.quota_cost || 1 }}</text>
						<text class="col col-time">{{ formatDate(item.created_at || item.created_at_text) }}</text>
						<view class="col col-action action-cell">
							<button class="mini-btn" @click="openEdit(item)">编辑</button>
							<button class="mini-btn danger-btn" @click="removeMessage(item)">删除</button>
						</view>
					</view>
				</view>
			</scroll-view>
			<view v-if="pagination.total > pagination.pageSize" class="message-pager">
				<button
					class="pager-btn"
					:class="isMessageFirstPage ? 'pager-btn is-disabled' : ''"
					@click="goMessagePrevPage"
				>
					上一页
				</button>
				<text class="pager-text">
					第 {{ pagination.page }} / {{ messageTotalPages }} 页
				</text>
				<button
					class="pager-btn"
					:class="isMessageLastPage ? 'pager-btn is-disabled' : ''"
					@click="goMessageNextPage"
				>
					下一页
				</button>
			</view>
		</view>
	</view>
</template>

<script>
let personnelUser = null

try {
	personnelUser = uniCloud.importObject('personnel-user')
} catch (error) {
	console.error('import personnel-user failed', error)
}

function createStats() {
	return {
		total: 0,
		draft: 0,
		queued: 0,
		delivered: 0,
		revoked: 0
	}
}

function createForm() {
	return {
		sender_record_id: '',
		receiver_record_id: '',
		content: '',
		user_remark: '',
		status: 'draft',
		quota_cost: '1',
		is_anonymous: true
	}
}

export default {
	data() {
		return {
			loading: false,
			candidateLoading: false,
			saving: false,
			records: [],
			candidateList: [],
			quotaInputs: {},
			stats: createStats(),
			messageKeyword: '',
			candidateKeyword: '',
			messageStatus: 'all',
			statusFilters: [
				{ label: '全部', value: 'all' },
				{ label: '草稿', value: 'draft' },
				{ label: '待投递', value: 'queued' },
				{ label: '已投递', value: 'delivered' },
				{ label: '已撤销', value: 'revoked' }
			],
			candidatePagination: {
				page: 1,
				pageSize: 5,
				total: 0
			},
			candidateSearchTimer: null,
			showQuotaPanel: false,
			pagination: {
				page: 1,
				pageSize: 6,
				total: 0
			},
			showForm: false,
			currentId: '',
			form: createForm()
		}
	},
	computed: {
		candidateLabels() {
			return this.candidateList.map((item) => item.label)
		},
		senderIndex() {
			return this.findCandidateIndex(this.form.sender_record_id)
		},
		receiverIndex() {
			return this.findCandidateIndex(this.form.receiver_record_id)
		},
		selectedSenderLabel() {
			const item = this.findCandidate(this.form.sender_record_id)
			return item ? item.label : '请选择发送方'
		},
		selectedReceiverLabel() {
			const item = this.findCandidate(this.form.receiver_record_id)
			return item ? item.label : '请选择接收方'
		},
		statusOptionLabels() {
			return this.statusFilters.slice(1).map((item) => item.label)
		},
		statusIndex() {
			const index = this.statusFilters.slice(1).findIndex((item) => item.value === this.form.status)
			return index > -1 ? index : 0
		},
		candidateTotalPages() {
			const pageSize = Number(this.candidatePagination.pageSize) || 5
			const total = Number(this.candidatePagination.total) || 0
			return Math.max(1, Math.ceil(total / pageSize))
		},
		isCandidateFirstPage() {
			return Number(this.candidatePagination.page || 1) <= 1
		},
		isCandidateLastPage() {
			return Number(this.candidatePagination.page || 1) >= this.candidateTotalPages
		},
		messageTotalPages() {
			const pageSize = Number(this.pagination.pageSize) || 6
			const total = Number(this.pagination.total) || 0
			return Math.max(1, Math.ceil(total / pageSize))
		},
		isMessageFirstPage() {
			return Number(this.pagination.page || 1) <= 1
		},
		isMessageLastPage() {
			return Number(this.pagination.page || 1) >= this.messageTotalPages
		}
	},
	watch: {
		candidateKeyword() {
			this.scheduleCandidateSearch()
		}
	},
	onLoad() {
		this.loadAll()
	},
	onUnload() {
		this.clearCandidateSearchTimer()
	},
	methods: {
		async loadAll() {
			await Promise.all([this.loadCandidates(1), this.loadMessages(1)])
		},
		goBack() {
			const pageStack = getCurrentPages()
			if (pageStack.length > 1) {
				uni.navigateBack({ delta: 1 })
				return
			}
			uni.reLaunch({ url: '/pkg/guide/hub' })
		},
		showUnavailable() {
			uni.showToast({ title: '云对象不可用', icon: 'none' })
		},
		findCandidate(id) {
			return this.candidateList.find((item) => item._id === id) || null
		},
		findCandidateIndex(id) {
			const index = this.candidateList.findIndex((item) => item._id === id)
			return index > -1 ? index : 0
		},
		toggleQuotaPanel() {
			this.showQuotaPanel = !this.showQuotaPanel
			if (this.showQuotaPanel && !this.candidateList.length && !this.candidateLoading) {
				this.loadCandidates(1)
			}
		},
		clearCandidateSearchTimer() {
			if (this.candidateSearchTimer) {
				clearTimeout(this.candidateSearchTimer)
				this.candidateSearchTimer = null
			}
		},
		scheduleCandidateSearch() {
			this.clearCandidateSearchTimer()
			this.candidateSearchTimer = setTimeout(() => {
				this.loadCandidates(1)
			}, 250)
		},
		async loadCandidates(page) {
			if (!personnelUser) {
				this.showUnavailable()
				return
			}
			this.candidateLoading = true
			try {
				const nextPage = Number(page) > 0 ? Number(page) : Number(this.candidatePagination.page || 1)
				const res = await personnelUser.listPrivateMessageCandidates({
					keyword: this.candidateKeyword,
					page: nextPage,
					pageSize: this.candidatePagination.pageSize
				})
				this.candidateList = Array.isArray(res && res.list) ? res.list : []
				this.candidatePagination = {
					page: Number((res && res.page) || nextPage || 1),
					pageSize: Number((res && res.pageSize) || this.candidatePagination.pageSize),
					total: Number((res && res.total) || 0)
				}
				const nextInputs = Object.assign({}, this.quotaInputs)
				this.candidateList.forEach((item) => {
					nextInputs[item._id] =
						typeof nextInputs[item._id] === 'string'
							? nextInputs[item._id]
							: String(item.private_message_quota || 0)
				})
				this.quotaInputs = nextInputs
			} catch (error) {
				uni.showToast({
					title: error.message || '参与者加载失败',
					icon: 'none'
				})
			} finally {
				this.candidateLoading = false
			}
		},
		async loadMessages(page) {
			if (!personnelUser) {
				this.showUnavailable()
				return
			}
			this.loading = true
			try {
				const res = await personnelUser.listHeartMessages({
					keyword: this.messageKeyword,
					status: this.messageStatus,
					page: page || this.pagination.page,
					pageSize: this.pagination.pageSize
				})
				this.records = Array.isArray(res && res.list) ? res.list : []
				this.pagination = {
					page: Number((res && res.page) || page || 1),
					pageSize: Number((res && res.pageSize) || this.pagination.pageSize),
					total: Number((res && res.total) || 0)
				}
				this.stats = Object.assign(createStats(), res && res.stats ? res.stats : {})
			} catch (error) {
				uni.showToast({
					title: error.message || '私信记录加载失败',
					icon: 'none'
				})
			} finally {
				this.loading = false
			}
		},
		changeStatus(value) {
			this.messageStatus = value
			this.searchMessages()
		},
		searchMessages() {
			this.loadMessages(1)
		},
		resetFilters() {
			this.messageKeyword = ''
			this.messageStatus = 'all'
			this.loadMessages(1)
		},
		onPageChange(event) {
			const current = Number(event && event.current)
			if (current > 0) {
				this.loadMessages(current)
			}
		},
		goMessagePrevPage() {
			if (this.isMessageFirstPage) {
				return
			}
			this.loadMessages(Number(this.pagination.page || 1) - 1)
		},
		goMessageNextPage() {
			if (this.isMessageLastPage) {
				return
			}
			this.loadMessages(Number(this.pagination.page || 1) + 1)
		},
		onCandidatePageChange(event) {
			const current = Number(event && event.current)
			if (current > 0) {
				this.loadCandidates(current)
			}
		},
		goCandidatePrevPage() {
			if (this.isCandidateFirstPage) {
				return
			}
			this.loadCandidates(Number(this.candidatePagination.page || 1) - 1)
		},
		goCandidateNextPage() {
			if (this.isCandidateLastPage) {
				return
			}
			this.loadCandidates(Number(this.candidatePagination.page || 1) + 1)
		},
		async changeQuota(item, mode) {
			if (!personnelUser || !item || !item._id) {
				return
			}
			const quotaValue = Number(this.quotaInputs[item._id])
			if (!Number.isInteger(quotaValue) || quotaValue < 0) {
				uni.showToast({ title: '请输入有效次数', icon: 'none' })
				return
			}
			try {
				await personnelUser.updatePrivateMessageQuota({
					id: item._id,
					quota: quotaValue,
					mode
				})
				uni.showToast({ title: '次数更新成功', icon: 'success' })
				await this.loadCandidates(this.candidatePagination.page)
			} catch (error) {
				uni.showToast({
					title: error.message || '次数更新失败',
					icon: 'none'
				})
			}
		},
		openCreate() {
			this.currentId = ''
			this.form = createForm()
			this.showForm = true
			uni.pageScrollTo({ scrollTop: 0, duration: 200 })
		},
		openEdit(item) {
			this.currentId = item._id
			this.form = {
				sender_record_id: item.sender_record_id || '',
				receiver_record_id: item.receiver_record_id || '',
				content: item.content || '',
				user_remark: item.user_remark || '',
				status: item.status || 'draft',
				quota_cost: String(item.quota_cost || 1),
				is_anonymous: item.is_anonymous !== false
			}
			this.showForm = true
			uni.pageScrollTo({ scrollTop: 0, duration: 200 })
		},
		closeForm() {
			this.showForm = false
			this.currentId = ''
			this.form = createForm()
		},
		resetForm() {
			this.currentId = ''
			this.form = createForm()
		},
		onSenderChange(event) {
			const item = this.candidateList[Number(event.detail.value)]
			this.form.sender_record_id = item ? item._id : ''
		},
		onReceiverChange(event) {
			const item = this.candidateList[Number(event.detail.value)]
			this.form.receiver_record_id = item ? item._id : ''
		},
		onStatusChange(event) {
			const item = this.statusFilters.slice(1)[Number(event.detail.value)]
			this.form.status = item ? item.value : 'draft'
		},
		onAnonymousChange(event) {
			this.form.is_anonymous = !!(event && event.detail && event.detail.value)
		},
		statusText(value) {
			const item = this.statusFilters.find((entry) => entry.value === value)
			return item ? item.label : '草稿'
		},
		validateForm() {
			if (!this.form.sender_record_id) {
				return '请选择发送方'
			}
			if (!this.form.receiver_record_id) {
				return '请选择接收方'
			}
			if (this.form.sender_record_id === this.form.receiver_record_id) {
				return '发送方和接收方不能是同一人'
			}
			if (!this.form.content) {
				return '请输入私信内容'
			}
			if (this.form.content.length > 300) {
				return '私信内容不能超过 300 字'
			}
			const quotaCost = Number(this.form.quota_cost)
			if (!Number.isInteger(quotaCost) || quotaCost < 1) {
				return '消耗次数至少为 1'
			}
			return ''
		},
		async submitForm() {
			if (!personnelUser) {
				this.showUnavailable()
				return
			}
			const errorMessage = this.validateForm()
			if (errorMessage) {
				uni.showToast({ title: errorMessage, icon: 'none' })
				return
			}
			if (this.saving) {
				return
			}
			this.saving = true
			const isEditMode = !!this.currentId
			try {
				const payload = {
					sender_record_id: this.form.sender_record_id,
					receiver_record_id: this.form.receiver_record_id,
					content: this.form.content,
					user_remark: this.form.user_remark,
					status: this.form.status,
					quota_cost: Number(this.form.quota_cost),
					is_anonymous: this.form.is_anonymous
				}
				if (isEditMode) {
					await personnelUser.updateHeartMessage({
						id: this.currentId,
						data: payload
					})
				} else {
					await personnelUser.createHeartMessage({
						data: payload
					})
				}
				uni.showToast({
					title: isEditMode ? '私信已更新' : '私信已创建',
					icon: 'success'
				})
				this.closeForm()
				await this.loadCandidates()
				await this.loadMessages(isEditMode ? this.pagination.page : 1)
			} catch (error) {
				uni.showToast({
					title: error.message || '保存失败',
					icon: 'none'
				})
			} finally {
				this.saving = false
			}
		},
		removeMessage(item) {
			if (!item || !item._id || !personnelUser) {
				return
			}
			uni.showModal({
				title: '确认删除',
				content: '删除后记录会被隐藏，但不会自动返还已扣减的私信次数，是否继续？',
				success: async (res) => {
					if (!res.confirm) {
						return
					}
					try {
						await personnelUser.removeHeartMessage({ id: item._id })
						uni.showToast({ title: '删除成功', icon: 'success' })
						await this.loadMessages(this.pagination.page)
					} catch (error) {
						uni.showToast({
							title: error.message || '删除失败',
							icon: 'none'
						})
					}
				}
			})
		},
		formatDate(value) {
			if (!value) {
				return '-'
			}
			const date = new Date(value)
			if (Number.isNaN(date.getTime())) {
				return typeof value === 'string' ? value.replace('T', ' ').slice(0, 16) : '-'
			}
			const year = date.getFullYear()
			const month = `${date.getMonth() + 1}`.padStart(2, '0')
			const day = `${date.getDate()}`.padStart(2, '0')
			const hours = `${date.getHours()}`.padStart(2, '0')
			const minutes = `${date.getMinutes()}`.padStart(2, '0')
			return `${year}-${month}-${day} ${hours}:${minutes}`
		}
	}
}
</script>

<style scoped lang="less">
.page {
	min-height: 100vh;
	padding: 24rpx;
	background: #f5efe5;
	box-sizing: border-box;
}

.toolbar,
.action-row,
.inline-actions,
.stats-wrap,
.candidate-item,
.candidate-actions,
.card-head,
.name-cell,
.action-cell,
.candidate-head,
.switch-field {
	display: flex;
	flex-wrap: wrap;
}

.toolbar,
.candidate-item,
.candidate-head {
	justify-content: space-between;
}

.toolbar,
.action-row,
.switch-field {
	align-items: center;
}

.space-between {
	justify-content: space-between;
	margin-top: 10rpx;
}

.hero-card,
.panel-card,
.stat-card {
	background: #fffcf7;
	border: 1rpx solid #eadfce;
	border-radius: 28rpx;
	box-shadow: 0 18rpx 40rpx rgba(91, 70, 40, 0.08);
}

.hero-card,
.panel-card {
	padding: 30rpx 28rpx;
}

.panel-card {
	margin-top: 24rpx;
}

.card-title,
.section-title {
	font-size: 32rpx;
	font-weight: 700;
	color: #2d241c;
}

.card-tip,
.secondary-text,
.candidate-meta {
	margin-top: 14rpx;
	font-size: 24rpx;
	line-height: 1.7;
	color: #716250;
}

.stats-wrap {
	display: flex;
	flex-wrap: nowrap;
	justify-content: space-between;
	gap: 16rpx;
	margin-top: 24rpx;
}

.stat-card {
	flex: 1;
	width: auto;
	min-width: 0;
	margin-bottom: 0;
	padding: 22rpx;
	box-sizing: border-box;
}

.stat-label {
	font-size: 24rpx;
	color: #7c6b57;
}

.stat-value {
	display: block;
	margin-top: 12rpx;
	font-size: 40rpx;
	font-weight: 700;
	color: #2e241b;
}

.search-input,
.input,
.picker,
.textarea,
.mini-input {
	width: 100%;
	background: #fbf8f2;
	border: 1rpx solid #dfd3c1;
	border-radius: 20rpx;
	box-sizing: border-box;
	font-size: 26rpx;
	color: #342b22;
}

.search-input,
.input,
.picker {
	height: 84rpx;
	line-height: 84rpx;
	padding: 0 24rpx;
}

.search-input {
	margin-top: 20rpx;
}

.textarea {
	min-height: 180rpx;
	padding: 20rpx 24rpx;
	line-height: 1.7;
}

.mini-input {
	width: 130rpx;
	height: 60rpx;
	line-height: 60rpx;
	padding: 0 16rpx;
	font-size: 24rpx;
}

.solid-btn,
.ghost-btn,
.light-btn,
.mini-btn {
	height: 76rpx;
	line-height: 76rpx;
	padding: 0 28rpx;
	border-radius: 999rpx;
	font-size: 26rpx;
	margin: 0 20rpx 0 0;
}

.solid-btn {
	background: #1f6b52;
	color: #ffffff;
}

.ghost-btn {
	background: #efe5d3;
	color: #6d4e2c;
}

.light-btn {
	background: #f7f1e6;
	color: #5b4a35;
}

.mini-btn {
	height: 60rpx;
	line-height: 60rpx;
	padding: 0 20rpx;
	font-size: 24rpx;
	background: #f3eadb;
	color: #5e472e;
	margin-right: 0;
}

.mini-ghost-btn {
	height: 60rpx;
	line-height: 60rpx;
	font-size: 24rpx;
	padding: 0 20rpx;
	margin-right: 0;
}

.danger-btn {
	background: #fde8e6;
	color: #b5483f;
}

.candidate-list {
	margin-top: 16rpx;
}

.quota-entry-row {
	margin-top: 20rpx;
}

.quota-panel {
	position: fixed;
	left: 50%;
	top: 50%;
	transform: translate(-50%, -50%);
	width: calc(100vw - 56rpx);
	max-width: 980rpx;
	max-height: 80vh;
	overflow-y: auto;
	margin-top: 0;
	padding: 24rpx;
	border-radius: 24rpx;
	background: #fffaf3;
	border: 1rpx solid #eadfce;
	box-shadow:
		0 0 0 100vmax rgba(44, 36, 28, 0.42),
		0 24rpx 56rpx rgba(91, 70, 40, 0.16);
	z-index: 40;
}

.candidate-pager {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 20rpx;
	margin-top: 16rpx;
	padding-top: 20rpx;
	border-top: 1rpx solid #eadfce;
}

.message-pager {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 20rpx;
	margin-top: 24rpx;
	padding-top: 20rpx;
	border-top: 1rpx solid #eadfce;
}

.pager-btn {
	display: flex;
	align-items: center;
	justify-content: center;
	min-width: 160rpx;
	height: 64rpx;
	line-height: 64rpx;
	padding: 0 24rpx;
	border-radius: 999rpx;
	font-size: 24rpx;
	color: #6d4e2c;
	background: #efe5d3;
	margin: 0;
}

.pager-btn.is-disabled {
	opacity: 0.45;
}

.pager-text {
	font-size: 24rpx;
	color: #7a6652;
}

.candidate-item {
	padding: 22rpx 0;
	border-bottom: 1rpx solid #eadfce;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.candidate-item:last-child {
	border-bottom: none;
}

.candidate-top,
.candidate-bottom {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 18rpx;
}

.candidate-main {
	flex: 1;
	min-width: 0;
}

.candidate-bottom-spacer {
	flex: 1;
	min-width: 0;
}

.candidate-name,
.primary-text {
	font-size: 28rpx;
	font-weight: 700;
	color: #2d241c;
}

.candidate-actions {
	align-items: center;
	justify-content: flex-end;
	width: 100%;
	gap: 12rpx;
}

.status-scroll {
	margin-top: 16rpx;
	white-space: nowrap;
}

.status-row {
	display: inline-flex;
	padding-bottom: 8rpx;
}

.status-chip {
	padding: 18rpx 28rpx;
	margin-right: 16rpx;
	border-radius: 999rpx;
	background: #f3ede1;
	color: #7d6546;
	font-size: 24rpx;
}

.status-chip.active {
	background: #2d654f;
	color: #ffffff;
}

.form-panel {
	margin-top: 24rpx;
	padding: 24rpx;
	border-radius: 24rpx;
	background: #fffaf3;
	border: 1rpx solid #eadfce;
}

.form-grid {
	margin-top: 20rpx;
}

.field {
	width: 100%;
	margin-bottom: 20rpx;
}

.field-full {
	width: 100%;
}

.switch-label {
	margin-bottom: 0;
}

.label {
	display: block;
	margin-bottom: 12rpx;
	font-size: 24rpx;
	color: #755f45;
}

.table-scroll {
	width: 100%;
	margin-top: 24rpx;
}

.table {
	min-width: 1480rpx;
}

.table-row {
	display: flex;
	align-items: stretch;
	border-bottom: 1rpx solid #eadfce;
}

.table-header {
	background: #f4ecde;
	border-radius: 20rpx 20rpx 0 0;
}

.body-row {
	background: rgba(255, 255, 255, 0.72);
}

.col {
	padding: 22rpx 16rpx;
	font-size: 24rpx;
	color: #46382b;
	box-sizing: border-box;
}

.col-status { width: 150rpx; }
.col-sender { width: 260rpx; }
.col-receiver { width: 260rpx; }
.col-content { width: 420rpx; }
.col-quota { width: 120rpx; }
.col-time { width: 220rpx; }
.col-action { width: 180rpx; }

.name-cell,
.action-cell,
.content-cell {
	flex-direction: column;
	justify-content: center;
}

.action-cell .mini-btn {
	margin-bottom: 12rpx;
}

.action-cell .mini-btn:last-child {
	margin-bottom: 0;
}

.status-pill {
	display: inline-block;
	padding: 10rpx 18rpx;
	border-radius: 999rpx;
	font-size: 22rpx;
}

.status-draft {
	background: #efe5d3;
	color: #6d4e2c;
}

.status-queued {
	background: #fff1cc;
	color: #8e6400;
}

.status-delivered {
	background: #dff4e8;
	color: #1e6b45;
}

.status-revoked {
	background: #fde2df;
	color: #a44239;
}

.content-text {
	font-size: 24rpx;
	line-height: 1.7;
	color: #2f251d;
	word-break: break-all;
	white-space: pre-wrap;
}

.empty-box {
	padding: 44rpx 24rpx;
	font-size: 26rpx;
	color: #857362;
	text-align: center;
}

</style>
