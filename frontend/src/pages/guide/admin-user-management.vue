<template>
	<view class="page">
		<view v-if="showCandidatePopup" class="candidate-popup-mask" @click="closeCandidatePopup">
			<view class="candidate-popup" @click.stop>
				<view class="candidate-head">
					<text class="section-title">选择人员加入用户</text>
					<button class="ghost-btn mini-ghost-btn" @click="closeCandidatePopup">关闭</button>
				</view>
				<input
					v-model.trim="candidateKeyword"
					class="search-input"
					placeholder="搜索候选人并提升为用户"
					confirm-type="search"
					@confirm="loadCandidateList"
				/>
				<view class="candidate-toolbar">
					<button class="light-btn" @click="loadCandidateList">查询候选人</button>
					<button class="ghost-btn" @click="goPersonnelManagement">去人员管理</button>
				</view>
				<view v-if="candidateLoading" class="empty-box">
					<text>正在加载候选人...</text>
				</view>
				<view v-else-if="!candidateList.length" class="empty-box">
					<text>暂无可提升的候选人</text>
				</view>
				<view v-else class="candidate-list">
					<view v-for="item in pagedCandidateList" :key="item._id" class="candidate-item">
						<view class="candidate-main">
							<text class="candidate-name">#{{ item.person_id }} · {{ item.nickname || '-' }} / {{ item.name || '-' }}</text>
							<text class="candidate-meta">手机：{{ item.mobile || '-' }}　MBTI：{{ item.mbti || '-' }}</text>
						</view>
						<button class="mini-btn" :disabled="actionLoading" @click="promoteToUser(item)">设为用户</button>
					</view>
					<view v-if="candidateList.length > candidatePagination.pageSize" class="candidate-pagination">
						<uni-pagination
							show-icon
							:current="candidatePagination.page"
							:page-size="candidatePagination.pageSize"
							:total="candidateList.length"
							@change="handleCandidatePageChange"
						/>
					</view>
				</view>
			</view>
		</view>

		<view class="toolbar">
			<button class="back-btn" @click="goBack">返回上一页</button>
		</view>

		<view v-if="accessChecked" class="panel-card user-card">
			<view class="card-head">
				<text class="card-title">用户管理</text>
				<text class="card-tip">默认只显示用户与高级用户；高级用户不可变更，普通用户可降级为普通测试者。</text>
			</view>

			<view class="stats-wrap">
				<view class="stat-card">
					<text class="stat-label">用户总数</text>
					<text class="stat-value">{{ userStats.total }}</text>
				</view>
				<view class="stat-card">
					<text class="stat-label">普通用户</text>
					<text class="stat-value">{{ userStats.users }}</text>
				</view>
				<view class="stat-card">
					<text class="stat-label">高级用户</text>
					<text class="stat-value">{{ userStats.superUsers }}</text>
				</view>
				<view class="stat-card">
					<text class="stat-label">候选人数</text>
					<text class="stat-value">{{ candidateList.length }}</text>
				</view>
			</view>

			<view class="toolbar-row">
				<input
					v-model.trim="userKeyword"
					class="search-input"
					placeholder="搜索编号 / 昵称 / 姓名 / 手机 / MBTI"
					confirm-type="search"
					@confirm="loadUserList"
				/>
				<view class="toolbar-actions">
					<button class="light-btn" @click="loadUserList">刷新</button>
					<button class="solid-btn" @click="openCandidatePopup">新增用户</button>
				</view>
			</view>

			<view v-if="showAddPanel" class="candidate-panel">
				<view class="candidate-head">
					<text class="section-title">选择人员加入用户</text>
					<button class="ghost-btn mini-ghost-btn" @click="toggleAddPanel">收起</button>
				</view>
				<input
					v-model.trim="candidateKeyword"
					class="search-input"
					placeholder="搜索普通测试者并提升为用户"
					confirm-type="search"
					@confirm="loadCandidateList"
				/>
				<view class="candidate-toolbar">
					<button class="light-btn" @click="loadCandidateList">查询候选人</button>
					<button class="ghost-btn" @click="goPersonnelManagement">去人员管理</button>
				</view>
				<view v-if="candidateLoading" class="empty-box">
					<text>正在加载候选人员...</text>
				</view>
				<view v-else-if="!candidateList.length" class="empty-box">
					<text>暂无可提升的普通测试者</text>
				</view>
				<view v-else class="candidate-list">
					<view v-for="item in pagedCandidateList" :key="item._id" class="candidate-item">
						<view class="candidate-main">
							<text class="candidate-name">#{{ item.person_id }} · {{ item.nickname || '-' }} / {{ item.name || '-' }}</text>
							<text class="candidate-meta">手机：{{ item.mobile || '-' }}　MBTI：{{ item.mbti || '-' }}</text>
						</view>
						<button class="mini-btn" :disabled="actionLoading" @click="promoteToUser(item)">设为用户</button>
					</view>
					<view v-if="candidateList.length > candidatePagination.pageSize" class="candidate-pagination">
						<uni-pagination
							show-icon
							:current="candidatePagination.page"
							:page-size="candidatePagination.pageSize"
							:total="candidateList.length"
							@change="handleCandidatePageChange"
						/>
					</view>
				</view>
			</view>

			<scroll-view scroll-x class="table-scroll">
				<view class="table">
					<view class="table-row table-header">
						<text class="col col-id">编号</text>
						<text class="col col-name">昵称 / 姓名</text>
						<text class="col col-mobile">手机号</text>
						<text class="col col-mbti">MBTI</text>
						<text class="col col-role">用户级别</text>
						<text class="col col-status">审核状态</text>
						<text class="col col-time">更新时间</text>
						<text class="col col-action">操作</text>
					</view>
					<view v-if="loading" class="empty-box">
						<text>正在加载用户数据...</text>
					</view>
					<view v-else-if="!userList.length" class="empty-box">
						<text>当前没有用户数据</text>
					</view>
					<view v-for="item in pagedUserList" :key="item._id" class="table-row body-row">
						<text class="col col-id">#{{ item.person_id || '-' }}</text>
						<view class="col col-name name-cell">
							<text class="primary-text">{{ item.nickname || '-' }}</text>
							<text class="secondary-text">{{ item.name || '-' }}</text>
						</view>
						<text class="col col-mobile">{{ item.mobile || '-' }}</text>
						<text class="col col-mbti">{{ item.mbti || '-' }}</text>
						<view class="col col-role">
							<text class="role-pill" :class="roleClass(item.user_role)">{{ userRoleText(item.user_role) }}</text>
						</view>
						<text class="col col-status">{{ reviewStatusText(item.review_status) }}</text>
						<text class="col col-time">{{ formatDate(item.updated_at || item.updated_at_text) }}</text>
						<view class="col col-action action-cell">
							<button
								v-if="Number(item.user_role) === 2"
								class="mini-btn danger-btn"
								:disabled="actionLoading"
								@click="demoteUser(item)"
							>
								降级为普通
							</button>
							<text v-else class="fixed-tip">高级用户不可变更</text>
						</view>
					</view>
					<view v-if="userList.length > userPagination.pageSize" class="table-pagination">
						<uni-pagination
							show-icon
							:current="userPagination.page"
							:page-size="userPagination.pageSize"
							:total="userList.length"
							@change="handleUserPageChange"
						/>
					</view>
				</view>
			</scroll-view>
		</view>
	</view>
</template>

<script>
import { personnelUserService as personnelUser } from '@/api/modules/personnel-user'
const PERSONNEL_PROFILE_STORAGE_KEY = 'mbtiPersonnelProfile'

export default {
	data() {
		return {
			currentUserRole: 0,
			accessChecked: false,
			loading: false,
			actionLoading: false,
			candidateLoading: false,
			showCandidatePopup: false,
			showAddPanel: false,
			userKeyword: '',
			candidateKeyword: '',
			userList: [],
			userPagination: {
				page: 1,
				pageSize: 8
			},
			candidateList: [],
			candidatePagination: {
				page: 1,
				pageSize: 5
			},
			userStats: {
				total: 0,
				users: 0,
				superUsers: 0
			}
		}
	},
	computed: {
		pagedUserList() {
			const page = Number(this.userPagination.page) || 1
			const pageSize = Number(this.userPagination.pageSize) || 8
			const start = (page - 1) * pageSize
			return this.userList.slice(start, start + pageSize)
		},
		pagedCandidateList() {
			const page = Number(this.candidatePagination.page) || 1
			const pageSize = Number(this.candidatePagination.pageSize) || 5
			const start = (page - 1) * pageSize
			return this.candidateList.slice(start, start + pageSize)
		}
	},
	onLoad() {
		this.currentUserRole = this.getCurrentUserRole()
		if (!this.ensurePageAccess()) {
			return
		}
		this.accessChecked = true
		this.loadUserList()
	},
	methods: {
		getCurrentUserRole() {
			try {
				const profile = uni.getStorageSync(PERSONNEL_PROFILE_STORAGE_KEY)
				return Number(profile && profile.user_role) || 0
			} catch (error) {
				console.error('getCurrentUserRole failed', error)
				return 0
			}
		},
		ensurePageAccess() {
			if (Number(this.currentUserRole) === 3) {
				return true
			}
			uni.showModal({
				title: '权限不足',
				content: '只有 user_role 为 3 的高级用户可以查看用户管理页面。',
				showCancel: false,
				success: () => {
					this.goBack()
				}
			})
			return false
		},
		goBack() {
			const pageStack = getCurrentPages()
			if (pageStack.length > 1) {
				uni.navigateBack({ delta: 1 })
				return
			}
			uni.reLaunch({ url: '/pkg/guide/hub' })
		},
		async loadUserList() {
			if (!this.accessChecked) {
				return
			}
			if (!personnelUser) {
				this.showUnavailable()
				return
			}
			this.loading = true
			try {
				const res = await personnelUser.listUsers({ keyword: this.userKeyword })
				this.userList = Array.isArray(res && res.list) ? res.list : []
				this.userPagination.page = 1
				this.userStats = {
					total: Number(res && res.stats && res.stats.total) || 0,
					users: Number(res && res.stats && res.stats.users) || 0,
					superUsers: Number(res && res.stats && res.stats.superUsers) || 0
				}
			} catch (error) {
				console.error('loadUserList failed', error)
				uni.showToast({
					title: error.message || '用户加载失败',
					icon: 'none'
				})
			} finally {
				this.loading = false
			}
		},
		handleUserPageChange(event) {
			const current = Number(event && event.current)
			this.userPagination.page = current > 0 ? current : 1
		},
		async loadCandidateList() {
			if (!this.accessChecked) {
				return
			}
			if (!personnelUser) {
				this.showUnavailable()
				return
			}
			this.candidateLoading = true
			try {
				const res = await personnelUser.listUserCandidates({ keyword: this.candidateKeyword })
				this.candidateList = Array.isArray(res && res.list) ? res.list : []
				this.candidatePagination.page = 1
			} catch (error) {
				console.error('loadCandidateList failed', error)
				uni.showToast({
					title: error.message || '候选人加载失败',
					icon: 'none'
				})
			} finally {
				this.candidateLoading = false
			}
		},
		toggleAddPanel(forceOpen) {
			const nextVisible = typeof forceOpen === 'boolean' ? forceOpen : !this.showAddPanel
			this.showAddPanel = nextVisible
			if (nextVisible) {
				this.candidatePagination.page = 1
				this.loadCandidateList()
			}
		},
		handleCandidatePageChange(event) {
			const current = Number(event && event.current)
			this.candidatePagination.page = current > 0 ? current : 1
		},
		openCandidatePopup() {
			this.showCandidatePopup = true
			this.candidatePagination.page = 1
			this.loadCandidateList()
		},
		closeCandidatePopup() {
			this.showCandidatePopup = false
		},
		async promoteToUser(item) {
			if (!this.accessChecked) {
				return
			}
			if (!item || !item._id || this.actionLoading || !personnelUser) {
				return
			}
			this.actionLoading = true
			try {
				await personnelUser.updateUserRole({ id: item._id, userRole: 2 })
				uni.showToast({ title: '已设为用户', icon: 'success' })
				await Promise.all([this.loadUserList(), this.loadCandidateList()])
			} catch (error) {
				console.error('promoteToUser failed', error)
				uni.showToast({
					title: error.message || '设置失败',
					icon: 'none'
				})
			} finally {
				this.actionLoading = false
			}
		},
		demoteUser(item) {
			if (!this.accessChecked) {
				return
			}
			if (!item || !item._id || Number(item.user_role) !== 2 || this.actionLoading || !personnelUser) {
				return
			}
			uni.showModal({
				title: '确认降级',
				content: `确认将 ${item.nickname || item.name || '该用户'} 降级为普通测试者吗？`,
				success: async (res) => {
					if (!res.confirm) {
						return
					}
					this.actionLoading = true
					try {
						await personnelUser.updateUserRole({ id: item._id, userRole: 0 })
						uni.showToast({ title: '已降级为普通', icon: 'success' })
						await Promise.all([this.loadUserList(), this.loadCandidateList()])
					} catch (error) {
						console.error('demoteUser failed', error)
						uni.showToast({
							title: error.message || '降级失败',
							icon: 'none'
						})
					} finally {
						this.actionLoading = false
					}
				}
			})
		},
		userRoleText(role) {
			const value = Number(role)
			if (value === 3) {
				return '高级用户'
			}
			if (value === 2) {
				return '用户'
			}
			return '普通测试者'
		},
		roleClass(role) {
			const value = Number(role)
			if (value === 3) {
				return 'role-super'
			}
			if (value === 2) {
				return 'role-user'
			}
			return 'role-normal'
		},
		reviewStatusText(status) {
			if (status === 'approved') {
				return '已通过'
			}
			if (status === 'rejected') {
				return '已驳回'
			}
			return '待审核'
		},
		formatDate(value) {
			if (!value) {
				return '-'
			}
			const date = new Date(value)
			if (Number.isNaN(date.getTime())) {
				return typeof value === 'string' ? value.replace('T', ' ').slice(0, 19) : '-'
			}
			const year = date.getFullYear()
			const month = `${date.getMonth() + 1}`.padStart(2, '0')
			const day = `${date.getDate()}`.padStart(2, '0')
			const hours = `${date.getHours()}`.padStart(2, '0')
			const minutes = `${date.getMinutes()}`.padStart(2, '0')
			return `${year}-${month}-${day} ${hours}:${minutes}`
		},
		goPersonnelManagement() {
			uni.navigateTo({ url: '/pkg/guide/roster' })
		},
		showUnavailable() {
			uni.showToast({ title: '云对象不可用', icon: 'none' })
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

.candidate-popup-mask {
	position: fixed;
	inset: 0;
	z-index: 40;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 28rpx;
	background: rgba(44, 36, 28, 0.45);
	box-sizing: border-box;
}

.candidate-popup {
	width: 100%;
	max-height: 86vh;
	padding: 24rpx;
	border-radius: 24rpx;
	background: #fffaf3;
	border: 1rpx solid #eadfce;
	box-shadow: 0 24rpx 56rpx rgba(91, 70, 40, 0.16);
	box-sizing: border-box;
	overflow-y: auto;
}

.toolbar {
	margin-bottom: 20rpx;
}

.back-btn {
	height: 68rpx;
	line-height: 68rpx;
	padding: 0 28rpx;
	border-radius: 999rpx;
	font-size: 24rpx;
	color: #6d4e2c;
	background: #efe5d3;
}

.panel-card,
.stat-card {
	background: #fffcf7;
	border: 1rpx solid #eadfce;
	border-radius: 28rpx;
	box-shadow: 0 18rpx 40rpx rgba(91, 70, 40, 0.08);
}

.panel-card {
	padding: 32rpx 28rpx;
}

.card-head {
	display: flex;
	flex-direction: column;
}

.card-title,
.section-title {
	font-size: 32rpx;
	font-weight: 700;
	color: #2d241c;
}

.card-tip,
.fixed-tip,
.secondary-text,
.candidate-meta {
	margin-top: 16rpx;
	font-size: 24rpx;
	line-height: 1.7;
	color: #716250;
}

.toolbar-row,
.toolbar-actions,
.candidate-head,
.candidate-toolbar,
.stats-wrap,
.action-cell {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
}

.candidate-head {
	justify-content: space-between;
}

.stats-wrap {
	justify-content: space-between;
	margin-top: 24rpx;
}

.stat-card {
	width: 48%;
	margin-bottom: 20rpx;
	padding: 24rpx;
	box-sizing: border-box;
}

.stat-label {
	font-size: 24rpx;
	color: #7c6b57;
}

.stat-value {
	margin-top: 12rpx;
	margin-left: 12rpx;
	font-size: 40rpx;
	font-weight: 700;
	color: #2e241b;
}

.toolbar-row {
	margin-top: 8rpx;
	align-items: flex-start;
}

.toolbar-actions,
.candidate-toolbar {
	justify-content: flex-end;
	margin-top: 20rpx;
}

.search-input {
	width: 100%;
	height: 84rpx;
	padding: 0 24rpx;
	line-height: 84rpx;
	background: #fbf8f2;
	border: 1rpx solid #dfd3c1;
	border-radius: 20rpx;
	box-sizing: border-box;
	color: #342b22;
	font-size: 26rpx;
}

.candidate-panel {
	margin-top: 24rpx;
	padding: 24rpx;
	border-radius: 24rpx;
	background: #fffaf3;
	border: 1rpx solid #eadfce;
}

.candidate-list {
	margin-top: 20rpx;
}

.candidate-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 1rpx solid #eadfce;
	gap: 20rpx;
}

.candidate-item:last-child {
	border-bottom: none;
}

.candidate-main {
	flex: 1;
	min-width: 0;
}

.candidate-name,
.primary-text {
	display: block;
	margin-top: 20rpx;
	font-size: 30rpx;
	font-weight: 700;
	color: #2d241c;
}

.candidate-pagination {
	margin-top: 24rpx;
	padding-top: 20rpx;
	border-top: 1rpx solid #eadfce;
	display: flex;
	justify-content: flex-end;
}

.table-scroll {
	width: 100%;
	margin-top: 24rpx;
}

.table-pagination {
	padding: 24rpx 0 8rpx;
	display: flex;
	justify-content: flex-end;
}

.table {
	min-width: 1280rpx;
}

.table-row {
	display: flex;
	flex-wrap: nowrap;
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
	white-space: nowrap;
}

.col-id { width: 120rpx; }
.col-name { width: 240rpx; }
.col-mobile { width: 220rpx; }
.col-mbti { width: 120rpx; }
.col-role {
	width: 190rpx;
	white-space: nowrap;
}
.col-status { width: 150rpx; }
.col-time { width: 220rpx; }
.col-action { width: 220rpx; }

.name-cell,
.action-cell {
	flex-direction: column;
	justify-content: flex-start;
}

.name-cell .primary-text,
.action-cell .fixed-tip {
	margin-top: 0;
}

.role-pill {
	display: inline-flex;
	align-items: center;
	padding: 10rpx 18rpx;
	border-radius: 999rpx;
	font-size: 22rpx;
	white-space: nowrap;
}

.role-user {
	background: #dff4e8;
	color: #1e6b45;
}

.role-super {
	background: #fce3ad;
	color: #7a4a12;
}

.role-normal {
	background: #efe5d3;
	color: #6d4e2c;
}

.empty-box {
	padding: 44rpx 24rpx;
	font-size: 26rpx;
	color: #857362;
	text-align: center;
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
</style>
