<template>
	<div class="page">
		<div class="hero">
			<div class="hero-backdrop hero-backdrop-left"></div>
			<div class="hero-backdrop hero-backdrop-right"></div>
			<div class="hero-copy">
				<text class="eyebrow">LOVE MBTI LAB</text>
				<text class="headline">Opening your home</text>
				<text class="subhead">We are checking your saved login profile.</text>
			</div>

			<div class="loading-card">
				<div class="loading-orb"></div>
				<text class="loading-text">{{ loadingText }}</text>
			</div>
		</div>
	</div>
</template>

<script>
import { app } from '@/platform/app-bridge'
import {
	LOGIN_PROFILE_HOME_PATHS,
	getLoginProfileFromStorage,
	resolveHomePathByLoginProfile
} from '@/utils/login-cookie'

export default {
	data() {
		return {
			loadingText: 'Checking login status...'
		}
	},
	async mounted() {
		await this.routeByLoginProfile()
	},
	methods: {
		updateLoadingText(targetUrl) {
			if (targetUrl === LOGIN_PROFILE_HOME_PATHS.admin) {
				this.loadingText = 'User detected, opening dashboard...'
			} else if (targetUrl === LOGIN_PROFILE_HOME_PATHS.user) {
				this.loadingText = 'Profile matched, opening navigation...'
			} else {
				this.loadingText = 'Opening login home...'
			}
		},
		async routeByLoginProfile() {
			const targetUrl = resolveHomePathByLoginProfile(getLoginProfileFromStorage())
			this.updateLoadingText(targetUrl)

			setTimeout(() => {
				app.reLaunch({
					url: targetUrl
				})
			}, 120)
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

.hero {
	position: relative;
	min-height: 100vh;
	padding: 56rpx 30rpx 48rpx;
	overflow: hidden;
	display: flex;
	flex-direction: column;
	justify-content: center;
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
.loading-card {
	position: relative;
	z-index: 2;
}

.eyebrow {
	display: block;
	font-size: 24rpx;
	letter-spacing: 6rpx;
	color: #8d5d41;
	margin-bottom: 16rpx;
	text-align: center;
}

.headline {
	display: block;
	font-size: 60rpx;
	line-height: 1.2;
	font-weight: 700;
	color: #2f211d;
	text-align: center;
}

.subhead {
	display: block;
	margin-top: 22rpx;
	font-size: 28rpx;
	line-height: 1.7;
	color: #6d5b56;
	text-align: center;
}

.loading-card {
	margin-top: 40rpx;
	padding: 42rpx 30rpx;
	border-radius: 36rpx;
	background: rgba(255, 255, 255, 0.78);
	box-shadow: 0 20rpx 44rpx rgba(117, 88, 63, 0.1);
	backdrop-filter: blur(10rpx);
	display: flex;
	flex-direction: column;
	align-items: center;
}

.loading-orb {
	width: 120rpx;
	height: 120rpx;
	border-radius: 50%;
	background: linear-gradient(180deg, #2f2a47 0%, #594a83 100%);
	box-shadow: 0 18rpx 32rpx rgba(77, 62, 109, 0.22);
	animation: pulse 1.2s ease-in-out infinite;
}

.loading-text {
	margin-top: 24rpx;
	font-size: 28rpx;
	color: #4e3d37;
	font-weight: 600;
}

@keyframes pulse {
	0%,
	100% {
		transform: scale(0.95);
		opacity: 0.7;
	}

	50% {
		transform: scale(1);
		opacity: 1;
	}
}

@media screen and (max-width: 420px) {
	.headline {
		font-size: 54rpx;
	}
}
</style>
