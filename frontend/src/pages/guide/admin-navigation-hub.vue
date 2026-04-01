<template>
	<div class="page">
		<div class="panel-card">
			<div class="card-head">
				<text class="card-title">后台功能导航</text>
				<text class="card-tip">点击模块卡片后进入对应管理页面。</text>
			</div>

			<div class="feature-grid">
				<div
					v-for="item in visibleFeatureList"
					:key="item.key"
					class="feature-card"
					@click="handleFeatureTap(item)"
				>
					<!-- <div class="feature-top">
						<text class="feature-tag">{{ formatModuleTag(index) }}</text>
						<text v-if="!item.available" class="feature-status is-pending">建设中</text>
						<text v-else class="feature-status is-ready">可用</text>
					</div> -->
					<text class="feature-title">{{ item.title }}</text>
					<text class="feature-desc">{{ item.desc }}</text>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
	import { app } from '@/platform/app-bridge'

	const PERSONNEL_PROFILE_STORAGE_KEY = 'mbtiPersonnelProfile'

	export default {
		data() {
			return {
				currentUserRole: 0,
				featureList: [
					{
						key: 'personnel-management',
						title: '人员管理',
						desc: '进入人员管理页面，维护参与者资料、审核状态与相关信息。',
						available: true,
						minUserRole: 1,
						url: '/pkg/guide/roster'
					},
					{
						key: 'mbti-pair-query',
						title: 'MBTI 组合配对查询',
						desc: '用于配置 MBTI 组合配对规则与查询展示结果。',
						available: true,
						minUserRole: 1,
						url: '/pkg/guide/insight'
					},
					{
						key: 'user-user',
						title: '用户管理',
						desc: '进入用户管理页面，维护用户、高级用户与候选人员。',
						available: true,
						minUserRole: 3,
						url: '/pkg/guide/panel'
					},
					{
						key: 'heart-message-manage',
						title: '心动私信管理',
						desc: '用于管理心动私信内容、发送关系与审核策略。',
						available: true,
						minUserRole: 1,
						url: '/pkg/guide/relay'
					},
					{
						key: 'match-vote-manage',
						title: '意向记录总览',
						desc: '用于查看活动内提交的排序记录与双向汇总结果。',
						available: true,
						minUserRole: 1,
						url: '/pkg/guide/intent'
					}
				]
			}
		},
		computed: {
			visibleFeatureList() {
				return this.featureList.filter((item) => this.hasFeatureAccess(item))
			}
		},
		onLoad() {
			this.currentUserRole = this.getCurrentUserRole()
		},
		methods: {
			getCurrentUserRole() {
				try {
					const profile = app.getStorageSync(PERSONNEL_PROFILE_STORAGE_KEY)
					return Number(profile && profile.user_role) || 0
				} catch (error) {
					console.error('getCurrentUserRole failed', error)
					return 0
				}
			},
			hasFeatureAccess(item) {
				if (!item) {
					return false
				}
				const requiredRole = Number(item.minUserRole || 0)
				return Number(this.currentUserRole) >= requiredRole
			},
			formatModuleTag(index) {
				const moduleNo = index + 1
				return `MODULE ${moduleNo < 10 ? `0${moduleNo}` : moduleNo}`
			},
			handleFeatureTap(item) {
				if (!this.hasFeatureAccess(item)) {
					app.showToast({ title: '当前权限不可访问', icon: 'none' })
					return
				}
				if (item && item.available && item.url) {
					app.navigateTo({ url: item.url })
					return
				}
				app.showToast({ title: '功能建设中', icon: 'none' })
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

	.panel-card,
	.feature-card {
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

	.card-title {
		font-size: 36rpx;
		font-weight: 700;
		color: #2d241c;
	}

	.card-tip,
	.feature-desc {
		margin-top: 16rpx;
		font-size: 24rpx;
		line-height: 1.7;
		color: #716250;
	}

	.feature-grid {
		margin-top: 24rpx;
	}

	.feature-card {
		padding: 28rpx 24rpx;
		margin-bottom: 20rpx;
	}

	.feature-top {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: space-between;
	}

	.feature-tag,
	.feature-status {
		padding: 10rpx 18rpx;
		border-radius: 999rpx;
		font-size: 22rpx;
	}

	.feature-tag {
		background: #f3eadb;
		color: #7b6244;
	}

	.feature-status.is-ready {
		background: #dff4e8;
		color: #1e6b45;
	}

	.feature-status.is-pending {
		background: #fff1cc;
		color: #8e6400;
	}

	.feature-title {
		display: block;
		margin-top: 20rpx;
		font-size: 32rpx;
		font-weight: 700;
		color: #2d241c;
	}
</style>
