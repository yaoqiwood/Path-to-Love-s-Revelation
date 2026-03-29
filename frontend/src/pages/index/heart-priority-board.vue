<template>
  <section class="priority-page">
    <section class="priority-shell">
      <div class="priority-glow priority-glow-left"></div>
      <div class="priority-glow priority-glow-right"></div>

      <header class="hero-copy">
        <p class="eyebrow">PATH TO LOVE</p>
        <h1 class="headline">心动优先榜</h1>
        <p class="subhead">把 24 位异性放进同一张心动地图里，排出你最想进一步了解的前 10 位。</p>
      </header>

      <section class="story-card">
        <p class="story-kicker">HOW IT WORKS</p>
        <h2 class="story-title">先看见顺序，再看见自己</h2>
        <p class="story-copy">
          这个功能适合在活动现场或统一资料池里使用。你会面对 24 位异性的候选资料，从中挑选出最想深入了解的
          10 位，并按优先级排列，最终形成一份只属于你的心动顺位。
        </p>
      </section>

      <section class="step-grid">
        <article class="step-card">
          <span class="step-no">01</span>
          <h3>浏览候选资料</h3>
          <p>从 24 位异性里逐一浏览，先形成整体印象。</p>
        </article>
        <article class="step-card">
          <span class="step-no">02</span>
          <h3>选出前 10 位</h3>
          <p>把最想进一步认识的人留下，逐步缩小范围。</p>
        </article>
        <article class="step-card">
          <span class="step-no">03</span>
          <h3>完成优先排序</h3>
          <p>从第 1 名到第 10 名排出你这一轮最真实的心动顺位。</p>
        </article>
      </section>

      <div class="action-row">
        <button class="primary-btn" type="button" disabled>功能即将开放</button>
        <button class="ghost-btn" type="button" @click="goBack">返回导航</button>
      </div>
    </section>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goBack() {
  router.push('/pages/index/home')
}
</script>

<style scoped lang="less">
.priority-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 10% 14%, rgba(255, 208, 177, 0.42), transparent 26%),
    radial-gradient(circle at 86% 20%, rgba(160, 214, 255, 0.34), transparent 24%),
    linear-gradient(180deg, #fffaf7 0%, #fff4ea 48%, #fff9f3 100%);
}

.priority-shell {
  position: relative;
  min-height: 100vh;
  padding: calc(44px + var(--safe-top, 0px)) clamp(22px, 5vw, 54px) calc(40px + var(--safe-bottom, 0px));
  overflow: hidden;
}

.priority-glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(18px);
  pointer-events: none;
}

.priority-glow-left {
  width: 220px;
  height: 220px;
  left: -86px;
  top: 42px;
  background: rgba(255, 185, 145, 0.36);
}

.priority-glow-right {
  width: 240px;
  height: 240px;
  right: -88px;
  top: 160px;
  background: rgba(151, 205, 255, 0.28);
}

.hero-copy,
.story-card,
.step-grid,
.action-row {
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
  font-size: clamp(40px, 6vw, 60px);
  line-height: 1.06;
}

.subhead {
  max-width: 34em;
  margin: 16px 0 0;
  color: #6f5c55;
  font-size: 16px;
  line-height: 1.85;
}

.story-card {
  margin-top: 28px;
  padding: 24px;
  border-radius: 30px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.84), rgba(255, 246, 239, 0.72)),
    linear-gradient(135deg, rgba(255, 235, 221, 0.86), rgba(255, 255, 255, 0.48));
  box-shadow: 0 24px 42px rgba(117, 88, 63, 0.1);
}

.story-kicker {
  margin: 0;
  color: #8a6c5f;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.18em;
}

.story-title {
  margin: 14px 0 0;
  color: #2f231f;
  font-size: 30px;
  line-height: 1.14;
}

.story-copy {
  margin: 14px 0 0;
  color: #6d5d57;
  font-size: 15px;
  line-height: 1.9;
}

.step-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: 20px;
}

.step-card {
  padding: 22px;
  border-radius: 26px;
  background: rgba(255, 255, 255, 0.74);
  box-shadow: 0 18px 32px rgba(117, 88, 63, 0.08);
}

.step-no {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2f2a47 0%, #6a588b 100%);
  color: #fff8ef;
  font-size: 14px;
  font-weight: 700;
}

.step-card h3 {
  margin: 16px 0 0;
  color: #302421;
  font-size: 24px;
}

.step-card p {
  margin: 10px 0 0;
  color: #6f615c;
  font-size: 14px;
  line-height: 1.8;
}

.action-row {
  display: flex;
  gap: 14px;
  margin-top: 22px;
}

.primary-btn,
.ghost-btn {
  min-height: 54px;
  padding: 0 24px;
  border: none;
  border-radius: 999px;
  font-size: 15px;
  font-weight: 700;
}

.primary-btn {
  flex: 1;
  background: linear-gradient(135deg, #2f2a47 0%, #5b4c88 55%, #7b5f83 100%);
  color: #fff7ef;
  opacity: 0.72;
  cursor: not-allowed;
}

.ghost-btn {
  background: rgba(255, 255, 255, 0.82);
  color: #4a3933;
  cursor: pointer;
}

@media (max-width: 900px) {
  .step-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .priority-shell {
    padding-left: 18px;
    padding-right: 18px;
  }

  .action-row {
    flex-direction: column;
  }
}
</style>
