<template>
	<view class="page">
		<view class="hero">
			<view class="hero-backdrop hero-backdrop-left"></view>
			<view class="hero-backdrop hero-backdrop-right"></view>

			<view class="hero-copy">
				<text class="eyebrow">LOVE MBTI TEST</text>
				<text class="headline">恋爱 MBTI 测试</text>
				<text class="subhead">12 种气质，88 道题。</text>
			</view>

			<view class="hero-stage">
				<view class="center-orb">
					<text class="orb-text">MBTI</text>
				</view>
				<view
					v-for="(item, index) in orbitTypes"
					:key="item.code"
					class="orbit-chip"
					:style="orbitStyle(index)"
				>
					<text class="orbit-chip-code">{{ item.code }}</text>
				</view>
			</view>

			<view class="hero-actions">
				<view class="hero-action-btn primary-btn" @click="goTest">
					<text>开始测试</text>
				</view>
				<view class="hero-action-btn ghost-btn" @click="scrollToGallery">
					<text>看人格</text>
				</view>
			</view>
		</view>

		<view class="stats-panel">
			<view class="stat-card">
				<text class="stat-label">人格</text>
				<text class="stat-value">12</text>
			</view>
			<view class="stat-card">
				<text class="stat-label">维度</text>
				<text class="stat-value">4</text>
			</view>
			<view class="stat-card">
				<text class="stat-label">题量</text>
				<text class="stat-value">88</text>
			</view>
		</view>

		<view class="gallery" id="gallery">
			<view class="section-head">
				<text class="section-kicker">PERSONAS</text>
				<text class="section-title">十二种心动人格</text>
				<text class="section-desc">先看哪一张最像你。</text>
			</view>

			<view class="card-grid">
				<view
					v-for="item in personas"
					:key="item.code"
					class="persona-card"
					:style="{ background: item.cardBg }"
				>
					<view class="persona-top">
						<view class="avatar-shell">
							<image class="avatar-image" :src="item.avatarBg" mode="aspectFit"></image>
						</view>
						<view class="persona-badge" :style="{ background: item.badgeBg }">
							<text class="persona-code">{{ item.code }}</text>
						</view>
					</view>
					<text class="persona-name">{{ item.name }}</text>
					<text class="persona-note">{{ item.note }}</text>
				</view>
			</view>
		</view>

		<view class="footer-cta">
			<text class="footer-title">准备好了就开始</text>
			<button class="primary-btn wide-btn" @click="goTest">进入测试</button>
		</view>
	</view>
</template>

<script>
	const personas = [
		{
			code: 'INFP',
			name: '月光理想家',
			note: '细腻温柔，重视共鸣。',
			cardBg: 'linear-gradient(160deg, #fff6f0 0%, #ffd7c2 100%)',
			avatarBg: '/static/mbti-personas/infp.svg',
			badgeBg: '#fff2e8'
		},
		{
			code: 'ENFP',
			name: '烟火冒险家',
			note: '热烈灵动，喜欢心动感。',
			cardBg: 'linear-gradient(160deg, #fff9e8 0%, #ffe29f 100%)',
			avatarBg: '/static/mbti-personas/enfp.svg',
			badgeBg: '#fff6cf'
		},
		{
			code: 'INFJ',
			name: '静谧预言家',
			note: '克制深情，擅长洞察。',
			cardBg: 'linear-gradient(160deg, #eef7ff 0%, #c9e7ff 100%)',
			avatarBg: '/static/mbti-personas/infj.svg',
			badgeBg: '#e8f5ff'
		},
		{
			code: 'ENFJ',
			name: '暖场指挥家',
			note: '温暖有力，擅长带动关系。',
			cardBg: 'linear-gradient(160deg, #f5efff 0%, #dcc8ff 100%)',
			avatarBg: '/static/mbti-personas/enfj.svg',
			badgeBg: '#f1eaff'
		},
		{
			code: 'INTP',
			name: '星图分析师',
			note: '理性冷静，也很有反差。',
			cardBg: 'linear-gradient(160deg, #edfdf6 0%, #c4f2dd 100%)',
			avatarBg: '/static/mbti-personas/intp.svg',
			badgeBg: '#e8fbf2'
		},
		{
			code: 'ENTP',
			name: '灵感煽动者',
			note: '机敏跳跃，喜欢新鲜感。',
			cardBg: 'linear-gradient(160deg, #fff3f7 0%, #ffc7d8 100%)',
			avatarBg: '/static/mbti-personas/entp.svg',
			badgeBg: '#ffe9f0'
		},
		{
			code: 'ISFP',
			name: '雾色艺术家',
			note: '慢热真心，偏爱细节。',
			cardBg: 'linear-gradient(160deg, #f7f4ef 0%, #ead7c1 100%)',
			avatarBg: '/static/mbti-personas/isfp.svg',
			badgeBg: '#f9f0e5'
		},
		{
			code: 'ESFP',
			name: '心动现场派',
			note: '活力直接，反馈很快。',
			cardBg: 'linear-gradient(160deg, #f2fff6 0%, #c8f7d4 100%)',
			avatarBg: '/static/mbti-personas/esfp.svg',
			badgeBg: '#e9ffef'
		},
		{
			code: 'ISTJ',
			name: '秩序守护者',
			note: '稳定可靠，喜欢兑现。',
			cardBg: 'linear-gradient(160deg, #f3f5f8 0%, #d6dde8 100%)',
			avatarBg: '/static/mbti-personas/istj.svg',
			badgeBg: '#eef2f7'
		},
		{
			code: 'ESTJ',
			name: '行动主理人',
			note: '直接果断，推动关系向前。',
			cardBg: 'linear-gradient(160deg, #fff4ec 0%, #ffd3b3 100%)',
			avatarBg: '/static/mbti-personas/estj.svg',
			badgeBg: '#fff0e4'
		},
		{
			code: 'INTJ',
			name: '冷焰策划者',
			note: '克制认真，目标感很强。',
			cardBg: 'linear-gradient(160deg, #eef1ff 0%, #c9d2ff 100%)',
			avatarBg: '/static/mbti-personas/intj.svg',
			badgeBg: '#ebeeff'
		},
		{
			code: 'ESFJ',
			name: '甜度组织者',
			note: '体贴周到，擅长经营氛围。',
			cardBg: 'linear-gradient(160deg, #fff8f3 0%, #ffe3d1 100%)',
			avatarBg: '/static/mbti-personas/esfj.svg',
			badgeBg: '#fff1e8'
		}
	]

	export default {
		data() {
			return {
				personas
			}
		},
		computed: {
			orbitTypes() {
				return this.personas.slice(0, 12)
			}
		},
		methods: {
			goTest() {
				uni.navigateTo({
					url: '/pages/user/helper'
				})
			},
			scrollToGallery() {
				const query = uni.createSelectorQuery().in(this)
				query.select('#gallery').boundingClientRect()
				query.selectViewport().scrollOffset()
				query.exec((res) => {
					const galleryRect = res && res[0]
					const viewport = res && res[1]
					if (!galleryRect || !viewport) {
						uni.showToast({
							title: '向下滑动查看人格',
							icon: 'none'
						})
						return
					}

					uni.pageScrollTo({
						scrollTop: galleryRect.top + viewport.scrollTop - 24,
						duration: 300
					})
				})
			},
			orbitStyle(index) {
				const positions = [
					{ top: '10rpx', left: '180rpx' },
					{ top: '70rpx', right: '30rpx' },
					{ top: '220rpx', right: '0rpx' },
					{ top: '360rpx', right: '70rpx' },
					{ top: '430rpx', left: '190rpx' },
					{ top: '360rpx', left: '40rpx' },
					{ top: '230rpx', left: '-10rpx' },
					{ top: '80rpx', left: '40rpx' },
					{ top: '30rpx', left: '320rpx' },
					{ top: '150rpx', right: '-10rpx' },
					{ top: '300rpx', left: '-20rpx' },
					{ top: '430rpx', right: '130rpx' }
				]
				return positions[index] || {}
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
		padding: 52rpx 30rpx 28rpx;
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
		top: 180rpx;
		background: linear-gradient(180deg, #cbe8ff 0%, #8ec8ff 100%);
	}

	.hero-copy,
	.hero-stage,
	.hero-actions,
	.stats-panel,
	.gallery,
	.footer-cta {
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
		font-size: 68rpx;
		line-height: 1.08;
		font-weight: 700;
		color: #2f211d;
	}

	.subhead {
		display: block;
		margin-top: 18rpx;
		font-size: 28rpx;
		line-height: 1.6;
		color: #6d5b56;
	}

	.hero-stage {
		position: relative;
		width: 520rpx;
		height: 520rpx;
		margin: 38rpx auto 26rpx;
		border-radius: 50%;
		border: 2rpx dashed rgba(111, 82, 66, 0.16);
	}

	.center-orb {
		position: absolute;
		left: 50%;
		top: 50%;
		width: 180rpx;
		height: 180rpx;
		margin-left: -90rpx;
		margin-top: -90rpx;
		border-radius: 50%;
		background: linear-gradient(180deg, #2f2a47 0%, #4b4266 100%);
		box-shadow: 0 24rpx 54rpx rgba(69, 56, 95, 0.22);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.orb-text {
		color: #fff6ec;
		font-size: 42rpx;
		font-weight: 700;
		letter-spacing: 4rpx;
	}

	.orbit-chip {
		position: absolute;
		min-width: 108rpx;
		padding: 14rpx 18rpx;
		border-radius: 999rpx;
		background: rgba(255, 255, 255, 0.76);
		backdrop-filter: blur(8rpx);
		box-shadow: 0 12rpx 24rpx rgba(87, 58, 37, 0.08);
		text-align: center;
	}

	.orbit-chip-code {
		font-size: 24rpx;
		font-weight: 700;
		color: #614536;
	}

	.hero-actions {
		display: flex;
		gap: 16rpx;
	}

	.hero-action-btn {
		flex: 1;
		height: 92rpx;
		border-radius: 999rpx;
		font-size: 30rpx;
		font-weight: 600;
		margin: 0;
		padding: 0;
		box-sizing: border-box;
		display: flex;
		align-items: center;
		justify-content: center;
		line-height: 1;
	}

	.hero-action-btn text {
		font-size: 30rpx;
		font-weight: 600;
		line-height: 1;
	}

	.primary-btn {
		background: linear-gradient(90deg, #2f2a47 0%, #594a83 100%);
		color: #fff9f0;
		box-shadow: 0 18rpx 32rpx rgba(77, 62, 109, 0.22);
	}

	.primary-btn::after,
	.ghost-btn::after,
	.wide-btn::after {
		border: none;
	}

	.ghost-btn {
		background: rgba(255, 255, 255, 0.68);
		color: #4e3d37;
		border: 2rpx solid rgba(94, 68, 54, 0.12);
	}

	.stats-panel {
		display: flex;
		padding: 0 30rpx;
		gap: 16rpx;
	}

	.stat-card {
		flex: 1;
		padding: 24rpx;
		border-radius: 28rpx;
		background: rgba(255, 255, 255, 0.72);
		box-shadow: 0 16rpx 34rpx rgba(117, 88, 63, 0.08);
	}

	.stat-label {
		display: block;
		font-size: 22rpx;
		color: #8f776d;
	}

	.stat-value {
		display: block;
		margin-top: 10rpx;
		font-size: 42rpx;
		font-weight: 700;
		color: #342925;
	}

	.gallery {
		padding: 26rpx 30rpx 10rpx;
	}

	.section-head {
		margin-bottom: 24rpx;
	}

	.section-kicker {
		display: block;
		font-size: 22rpx;
		letter-spacing: 4rpx;
		color: #8e6a53;
		margin-bottom: 12rpx;
	}

	.section-title {
		display: block;
		font-size: 46rpx;
		font-weight: 700;
		color: #2f231f;
	}

	.section-desc {
		display: block;
		margin-top: 12rpx;
		font-size: 28rpx;
		line-height: 1.6;
		color: #6f615c;
	}

	.card-grid {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
	}

	.persona-card {
		width: 332rpx;
		padding: 22rpx;
		margin-bottom: 20rpx;
		border-radius: 32rpx;
		min-height: 296rpx;
		box-shadow: 0 18rpx 32rpx rgba(117, 88, 63, 0.1);
	}

	.persona-top {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		margin-bottom: 18rpx;
	}

	.avatar-shell {
		position: relative;
		width: 132rpx;
		height: 148rpx;
		border-radius: 28rpx;
		overflow: hidden;
		background: rgba(255, 255, 255, 0.56);
		box-shadow: inset 0 0 0 2rpx rgba(255, 255, 255, 0.35);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.avatar-image {
		width: 124rpx;
		height: 140rpx;
	}

	.persona-badge {
		padding: 10rpx 14rpx;
		border-radius: 999rpx;
	}

	.persona-code {
		font-size: 22rpx;
		font-weight: 700;
		color: #4c372f;
	}

	.persona-name {
		display: block;
		font-size: 34rpx;
		font-weight: 700;
		color: #2c211e;
		line-height: 1.3;
	}

	.persona-note {
		display: block;
		margin-top: 12rpx;
		font-size: 24rpx;
		line-height: 1.6;
		color: #4a3d37;
	}

	.footer-cta {
		margin: 18rpx 30rpx 48rpx;
		padding: 30rpx;
		border-radius: 36rpx;
		background: linear-gradient(180deg, #2f2a47 0%, #40355f 100%);
		box-shadow: 0 24rpx 40rpx rgba(57, 45, 83, 0.22);
	}

	.footer-title {
		display: block;
		margin-bottom: 22rpx;
		font-size: 42rpx;
		font-weight: 700;
		color: #fff7ef;
	}

	.wide-btn {
		width: 100%;
		height: 92rpx;
		border-radius: 999rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	@media screen and (max-width: 420px) {
		.headline {
			font-size: 58rpx;
		}

		.hero-stage {
			width: 480rpx;
			height: 480rpx;
		}

		.card-grid,
		.stats-panel,
		.hero-actions {
			display: block;
		}

		.persona-card,
		.stat-card,
		.hero-action-btn {
			width: 100%;
		}

		.stat-card + .stat-card,
		.hero-action-btn + .hero-action-btn {
			margin-top: 18rpx;
		}
	}
</style>
