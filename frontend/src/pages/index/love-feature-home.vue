<template>
	<section class="feature-page">
		<section class="feature-shell">
			<div class="page-glow page-glow-left"></div>
			<div class="page-glow page-glow-right"></div>
			<div class="page-wave page-wave-top"></div>

			<header class="hero-copy">
				<p class="eyebrow">PATH TO LOVE</p>
				<h1 class="headline">爱的导航台</h1>
				<p class="subhead">从这里开始测试、进入信号小屋，或排出这一轮最想进一步了解的心动坐标。</p>
			</header>

			<section class="profile-strip">
				<div class="profile-pill">
					<span class="profile-label">当前身份</span>
					<strong>{{ displayName }}</strong>
				</div>
				<div class="profile-pill">
					<span class="profile-label">编号</span>
					<strong>#{{ profile.person_id || '--' }}</strong>
				</div>
				<div class="profile-pill profile-pill-wide">
					<span class="profile-label">状态</span>
					<strong>{{ mbtiStatus }}</strong>
				</div>
			</section>

			<section class="feature-grid">
				<article
					v-for="(card, index) in visibleFeatureCards"
					:key="card.key"
					:class="['feature-card', card.cardClass]"
				>
					<p class="card-kicker">{{ formatModuleLabel(index) }}</p>
					<h2 class="card-title">{{ card.title }}</h2>
					<p class="card-copy">{{ card.copy }}</p>
					<button :class="['card-btn', card.buttonClass]" type="button" @click="card.onClick">
						{{ card.buttonText }}
					</button>
				</article>
			</section>
		</section>
	</section>
</template>

<script setup>
	import { computed, reactive } from 'vue'
	import { useRouter } from 'vue-router'
	import { getLoginProfileFromStorage } from '@/utils/login-cookie'

	const router = useRouter()
	const profile = reactive(getStoredProfile())

	const displayName = computed(() => {
		const nickname = String(profile.nickname || '').trim()
		const name = String(profile.name || '').trim()
		return nickname || name || '爱的来宾'
	})
	const mbtiStatus = computed(() => {
		const mbti = String(profile.mbti || '').trim()

		return mbti || '未完成测试'
	})
	const shouldShowMbtiTestCard = computed(() => !String(profile.mbti || '').trim())
	const visibleFeatureCards = computed(() =>
		[
			shouldShowMbtiTestCard.value
				? {
						key: 'mbti-test',
						title: 'MBTI 测试',
						copy: '重新进入测试流程，查看你在关系里的节奏、偏好与吸引方向。',
						buttonText: '开始测试',
						cardClass: 'feature-card-primary',
						buttonClass: 'card-btn-primary',
						onClick: goMbtiTest
					}
				: null,
			{
				key: 'signal-cabin',
				title: '信号小屋',
				copy: '进入聊天功能的信号小屋，查看消息、开启对话，慢慢靠近你想认识的人。',
				buttonText: '进入小屋',
				cardClass: '',
				buttonClass: '',
				onClick: goSignalCabin
			},
			{
				key: 'heart-coordinate',
				title: '心动坐标',
				copy: '男生和女生分别从 24 位异性里选出自己最想了解的 10 个人，并完成一份带顺序的心动排序。',
				buttonText: '查看入口',
				cardClass: 'feature-card-accent',
				buttonClass: '',
				onClick: goHeartCoordinate
			}
		].filter(Boolean)
	)

	function getStoredProfile() {
		return getLoginProfileFromStorage() || {}
	}

	function formatModuleLabel(index) {
		return `MODULE ${String(index + 1).padStart(2, '0')}`
	}

	function goMbtiTest() {
		const query = []
		if (profile.name) {
			query.push(`name=${encodeURIComponent(profile.name)}`)
		}
		if (profile.personnel_id || profile.id) {
			query.push(`personnelId=${encodeURIComponent(profile.personnel_id || profile.id)}`)
		}

		router.push(query.length ? `/pages/feed/entry?${query.join('&')}` : '/pages/feed/entry')
	}

	function goSignalCabin() {
		router.push('/pkg/guide/detail')
	}

	function goHeartCoordinate() {
		router.push('/pages/index/heart-priority-board')
	}
</script>

<style scoped lang="less">
	.feature-page {
		min-height: 100vh;
		background:
			radial-gradient(circle at 12% 14%, rgba(255, 205, 170, 0.45), transparent 26%),
			radial-gradient(circle at 88% 18%, rgba(133, 199, 255, 0.34), transparent 24%),
			linear-gradient(180deg, #fffaf6 0%, #fff4ea 46%, #fffaf4 100%);
	}

	.feature-shell {
		position: relative;
		min-height: 100vh;
		padding: calc(44px + var(--safe-top, 0px)) clamp(22px, 5vw, 54px)
			calc(40px + var(--safe-bottom, 0px));
		overflow: hidden;
	}

	.page-glow,
	.page-wave {
		position: absolute;
		pointer-events: none;
	}

	.page-glow {
		border-radius: 999px;
		filter: blur(18px);
	}

	.page-glow-left {
		width: 220px;
		height: 220px;
		left: -92px;
		top: 32px;
		background: rgba(255, 187, 140, 0.4);
	}

	.page-glow-right {
		width: 240px;
		height: 240px;
		right: -84px;
		top: 160px;
		background: rgba(139, 200, 255, 0.32);
	}

	.page-wave-top {
		top: -120px;
		left: 50%;
		width: min(92vw, 820px);
		height: 300px;
		margin-left: calc(min(92vw, 820px) / -2);
		border-radius: 50%;
		background:
			radial-gradient(circle at center, rgba(255, 255, 255, 0.86), transparent 62%),
			linear-gradient(180deg, rgba(255, 244, 235, 0.64), rgba(255, 255, 255, 0));
	}

	.hero-copy,
	.profile-strip,
	.feature-grid {
		position: relative;
		z-index: 2;
	}

	.eyebrow {
		margin: 0;
		color: #8f6247;
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.3em;
		text-transform: uppercase;
	}

	.headline {
		margin: 14px 0 0;
		color: #2d211d;
		font-family: var(--font-display);
		font-size: clamp(42px, 7vw, 64px);
		line-height: 1.04;
	}

	.subhead {
		max-width: 32em;
		margin: 16px 0 0;
		color: #6f5c55;
		font-size: 16px;
		line-height: 1.8;
	}

	.profile-strip {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 12px;
		margin-top: 24px;
		align-items: center;
	}

	.profile-pill {
		min-height: 0;
		padding: 12px 16px;
		border-radius: 18px;
		background: rgba(255, 255, 255, 0.58);
		border: 1px solid rgba(255, 255, 255, 0.62);
		box-shadow: 0 10px 20px rgba(117, 88, 63, 0.06);
		backdrop-filter: blur(10px);
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
	}

	.profile-label {
		color: #92756a;
		font-size: 12px;
		letter-spacing: 0.06em;
		white-space: nowrap;
	}

	.profile-pill strong {
		color: #322521;
		font-size: clamp(15px, 1.8vw, 18px);
		line-height: 1.2;
		text-align: right;
	}

	.profile-pill-wide {
		grid-column: 1 / -1;
	}

	.feature-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 20px;
		margin-top: 28px;
		align-items: stretch;
	}

	.feature-card {
		position: relative;
		min-height: 320px;
		padding: 26px 24px 24px;
		border-radius: 32px;
		border: 1px solid rgba(255, 255, 255, 0.52);
		background:
			linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(255, 247, 239, 0.74)),
			linear-gradient(135deg, rgba(255, 238, 227, 0.8), rgba(255, 255, 255, 0.52));
		box-shadow:
			0 24px 44px rgba(117, 88, 63, 0.1),
			inset 0 1px 0 rgba(255, 255, 255, 0.72);
		display: flex;
		flex-direction: column;
		overflow: hidden;
		transition:
			transform 0.22s ease,
			box-shadow 0.22s ease,
			border-color 0.22s ease;
	}

	.feature-card::before {
		content: '';
		position: absolute;
		inset: 0 auto auto 0;
		width: 100%;
		height: 96px;
		background: linear-gradient(180deg, rgba(255, 255, 255, 0.24), rgba(255, 255, 255, 0));
		pointer-events: none;
	}

	.feature-card::after {
		content: '';
		position: absolute;
		left: 24px;
		right: 24px;
		top: 0;
		height: 4px;
		border-radius: 999px;
		background: linear-gradient(90deg, rgba(255, 183, 142, 0.82), rgba(117, 94, 160, 0.72));
	}

	.feature-card:hover {
		transform: translateY(-4px);
		border-color: rgba(255, 255, 255, 0.72);
		box-shadow:
			0 30px 52px rgba(117, 88, 63, 0.14),
			inset 0 1px 0 rgba(255, 255, 255, 0.78);
	}

	.feature-card-primary {
		background:
			linear-gradient(180deg, rgba(48, 42, 72, 0.95), rgba(84, 70, 126, 0.92)),
			linear-gradient(145deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.02));
		border-color: rgba(255, 255, 255, 0.12);
	}

	.feature-card-accent {
		background:
			linear-gradient(180deg, rgba(255, 248, 241, 0.92), rgba(255, 239, 230, 0.84)),
			radial-gradient(circle at top right, rgba(255, 189, 156, 0.3), transparent 44%);
	}

	.card-kicker {
		margin: 0;
		color: rgba(111, 92, 84, 0.82);
		font-size: 11px;
		font-weight: 700;
		letter-spacing: 0.22em;
		position: relative;
		z-index: 1;
	}

	.feature-card-primary .card-kicker,
	.feature-card-primary .card-title,
	.feature-card-primary .card-copy {
		color: #fff7ef;
	}

	.card-title {
		margin: 18px 0 0;
		color: #2f231f;
		font-size: clamp(30px, 3vw, 36px);
		line-height: 1.06;
		position: relative;
		z-index: 1;
	}

	.card-copy {
		margin: 14px 0 0;
		color: #6d5d57;
		font-size: 15px;
		line-height: 1.85;
		word-break: break-word;
		position: relative;
		z-index: 1;
	}

	.card-btn {
		margin-top: auto;
		min-height: 54px;
		padding: 0 20px;
		border: none;
		border-radius: 999px;
		background: rgba(255, 255, 255, 0.8);
		color: #43322c;
		font-size: 15px;
		font-weight: 700;
		cursor: pointer;
		position: relative;
		z-index: 1;
		transition:
			transform 0.22s ease,
			box-shadow 0.22s ease,
			filter 0.22s ease;
	}

	.card-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 16px 26px rgba(100, 76, 58, 0.14);
	}

	.card-btn-primary {
		background: rgba(255, 248, 239, 0.14);
		color: #fff7ef;
		box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.18);
	}

	@media (max-width: 1200px) {
		.feature-grid {
			grid-template-columns: none;
			grid-auto-flow: column;
			grid-auto-columns: minmax(248px, 280px);
			overflow-x: auto;
			padding-bottom: 6px;
			padding-right: 6px;
			scrollbar-width: none;
			scroll-snap-type: x proximity;
		}

		.feature-grid::-webkit-scrollbar {
			display: none;
		}

		.feature-card {
			min-height: 286px;
			scroll-snap-align: start;
		}
	}

	@media (max-width: 960px) {
		.profile-strip {
			gap: 10px;
		}

		.profile-pill {
			padding: 11px 14px;
		}
	}

	@media (max-width: 640px) {
		.feature-shell {
			padding-left: 18px;
			padding-right: 18px;
		}

		.profile-strip {
			gap: 8px;
		}

		.profile-pill {
			padding: 10px 12px;
			border-radius: 16px;
			gap: 8px;
		}

		.profile-label {
			font-size: 11px;
			letter-spacing: 0.04em;
		}

		.profile-pill strong {
			font-size: 14px;
		}

		.feature-grid {
			grid-auto-columns: minmax(226px, 248px);
			gap: 16px;
		}

		.feature-card {
			min-height: 272px;
			padding: 22px 20px 20px;
			border-radius: 28px;
		}

		.card-title {
			font-size: 32px;
		}

		.card-copy {
			font-size: 14px;
			line-height: 1.72;
		}

		.card-btn {
			min-height: 50px;
		}
	}
</style>

