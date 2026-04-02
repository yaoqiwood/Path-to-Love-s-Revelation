<template>
	<section class="not-found-page">
		<div class="glow glow-left"></div>
		<div class="glow glow-right"></div>

		<section class="hero">
			<p class="eyebrow">PATH TO LOVE</p>
			<p class="code-mark">404</p>
			<h1 class="headline">这个页面没有找到</h1>
			<p class="subhead">
				你访问的地址可能不存在，或者当前站点中还没有对应的页面内容。
			</p>

			<div class="hero-actions">
				<button class="hero-action-btn primary-btn" type="button" @click="goWelcome">
					回到欢迎页
				</button>
				<button class="hero-action-btn secondary-btn" type="button" @click="goBack">
					返回上一页
				</button>
			</div>
		</section>
	</section>
</template>

<script setup>
	import { useRouter } from 'vue-router'

	const router = useRouter()

	function goWelcome() {
		router.push('/welcome')
	}

	function goBack() {
		if (typeof window !== 'undefined' && window.history.length > 1) {
			router.back()
			return
		}

		router.push('/welcome')
	}
</script>

<style scoped lang="less">
	.not-found-page {
		position: relative;
		min-height: 100vh;
		overflow: hidden;
		background:
			radial-gradient(circle at top left, rgba(255, 204, 177, 0.5), transparent 28%),
			radial-gradient(circle at 85% 18%, rgba(170, 221, 255, 0.32), transparent 26%),
			linear-gradient(180deg, #fff9f4 0%, #fff3ea 48%, #fffaf5 100%);
	}

	.glow {
		position: absolute;
		border-radius: 999px;
		filter: blur(18px);
		opacity: 0.5;
		pointer-events: none;
	}

	.glow-left {
		top: -100px;
		left: -60px;
		width: 240px;
		height: 240px;
		background: rgba(255, 183, 137, 0.46);
	}

	.glow-right {
		right: -70px;
		bottom: -90px;
		width: 280px;
		height: 280px;
		background: rgba(122, 187, 255, 0.22);
	}

	.hero {
		position: relative;
		z-index: 1;
		min-height: 100vh;
		padding: calc(72px + var(--safe-top, 0px)) 24px calc(40px + var(--safe-bottom, 0px));
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
	}

	.eyebrow {
		margin: 0;
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.3em;
		text-transform: uppercase;
		color: #8d5d41;
	}

	.code-mark {
		margin: 18px 0 0;
		font-size: clamp(68px, 18vw, 144px);
		line-height: 0.9;
		font-weight: 800;
		color: #b55733;
		text-shadow: 0 16px 34px rgba(181, 87, 51, 0.18);
	}

	.headline {
		margin: 18px 0 0;
		font-size: clamp(32px, 7vw, 56px);
		line-height: 1.04;
		color: #2b1d19;
		font-family: var(--font-display);
	}

	.subhead {
		max-width: 34em;
		margin: 18px 0 0;
		font-size: 16px;
		line-height: 1.9;
		color: #6d5b56;
	}

	.hero-actions {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 14px;
		margin-top: 28px;
	}

	.hero-action-btn {
		min-width: 148px;
		height: 50px;
		padding: 0 22px;
		border-radius: 999px;
		font-size: 15px;
		font-weight: 700;
		cursor: pointer;
		transition:
			transform 0.2s ease,
			box-shadow 0.2s ease;
	}

	.hero-action-btn:hover {
		transform: translateY(-1px);
	}

	.primary-btn {
		border: none;
		color: #fff8f3;
		background: linear-gradient(135deg, #d07c43 0%, #b55632 100%);
		box-shadow: 0 18px 34px rgba(181, 86, 50, 0.24);
	}

	.secondary-btn {
		border: 1px solid rgba(141, 93, 65, 0.18);
		color: #5d4838;
		background: rgba(255, 255, 255, 0.82);
	}

	@media (max-width: 640px) {
		.hero {
			padding-inline: 18px;
		}

		.hero-action-btn {
			width: 100%;
		}
	}
</style>
