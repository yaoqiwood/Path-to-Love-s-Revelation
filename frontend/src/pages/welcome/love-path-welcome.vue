<template>
  <section class="welcome-page">
    <section class="hero">
      <div class="hero-glow hero-glow-top"></div>
      <div class="hero-glow hero-glow-bottom"></div>
      <div class="hero-backdrop hero-backdrop-left"></div>
      <div class="hero-backdrop hero-backdrop-right"></div>

      <div class="hero-copy">
        <p class="eyebrow">PATH TO LOVE</p>
        <h1 class="headline">
          <span class="headline-line">欢迎来到</span>
          <span class="headline-line">爱的启示“路”</span>
        </h1>
        <p class="subhead">先看见自己，再靠近彼此。</p>
        <p class="hero-intro">
          在性格、吸引与表达之间，慢慢找到最贴近自己的那条关系路径。
        </p>
      </div>

      <div class="hero-stage">
        <div class="center-orb">
          <span class="orb-text">LOVE</span>
        </div>
        <div
          v-for="(item, index) in orbitTypes"
          :key="item.code"
          class="orbit-chip"
          :style="orbitStyle(index)"
        >
          <span class="orbit-chip-code">{{ item.code }}</span>
        </div>
      </div>

      <div class="hero-actions">
        <button class="hero-action-btn primary-btn" type="button" @click="enterLovePath">
          进入爱之路
        </button>
      </div>
    </section>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const orbitTypes = [
  { code: 'INFP' },
  { code: 'ENFP' },
  { code: 'INFJ' },
  { code: 'ENFJ' },
  { code: 'INTJ' },
  { code: 'INTP' },
  { code: 'ENTJ' },
  { code: 'ISTJ' },
  { code: 'ESFP' },
  { code: 'ISFP' },
  { code: 'ENTP' },
  { code: 'ISFJ' }
]

function orbitStyle(index) {
  const positions = [
    { top: '-12px', left: '138px' },
    { top: '8px', right: '72px' },
    { top: '66px', right: '8px' },
    { top: '148px', right: '-8px' },
    { top: '212px', right: '24px' },
    { top: '254px', right: '92px' },
    { top: '268px', left: '138px' },
    { top: '254px', left: '92px' },
    { top: '212px', left: '24px' },
    { top: '148px', left: '-8px' },
    { top: '66px', left: '8px' },
    { top: '8px', left: '72px' }
  ]

  return positions[index] || {}
}

function enterLovePath() {
  router.push('/pages/index/login-home')
}
</script>

<style scoped lang="less">
.welcome-page {
  min-height: 100vh;
  padding: 0;
  background:
    radial-gradient(circle at top left, rgba(255, 204, 177, 0.48), transparent 30%),
    radial-gradient(circle at 85% 16%, rgba(170, 221, 255, 0.38), transparent 22%),
    radial-gradient(circle at 50% 52%, rgba(255, 255, 255, 0.78), transparent 34%),
    linear-gradient(180deg, #fffaf5 0%, #fff2e8 44%, #fff8f1 100%);
}

.hero {
  position: relative;
  overflow: hidden;
  min-height: 100vh;
  padding: calc(56px + var(--safe-top, 0px)) clamp(22px, 5vw, 52px) calc(40px + var(--safe-bottom, 0px));
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.7), rgba(255, 247, 240, 0.4)),
    linear-gradient(180deg, rgba(255, 255, 255, 0.22), rgba(255, 255, 255, 0.08));
  backdrop-filter: blur(18px);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.hero-glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(10px);
  pointer-events: none;
}

.hero-glow-top {
  width: 260px;
  height: 260px;
  top: -120px;
  right: 12%;
  background: radial-gradient(circle, rgba(255, 228, 210, 0.88), transparent 72%);
}

.hero-glow-bottom {
  width: 280px;
  height: 280px;
  left: -90px;
  bottom: -120px;
  background: radial-gradient(circle, rgba(255, 203, 164, 0.42), transparent 72%);
}

.hero-backdrop {
  position: absolute;
  border-radius: 999px;
  filter: blur(10px);
  opacity: 0.55;
}

.hero-backdrop-left {
  width: 180px;
  height: 180px;
  left: -74px;
  top: -18px;
  background: linear-gradient(180deg, #ffd5bc 0%, #ffb58b 100%);
}

.hero-backdrop-right {
  width: 164px;
  height: 164px;
  right: -52px;
  top: 146px;
  background: linear-gradient(180deg, #cbe8ff 0%, #8ec8ff 100%);
}

.hero-copy,
.hero-stage,
.hero-actions {
  position: relative;
  z-index: 2;
}

.eyebrow {
  display: block;
  color: #8d5d41;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  font-size: 12px;
  font-weight: 700;
}

.headline {
  max-width: 8em;
  margin: 14px 0 0;
  color: #2b1d19;
  font-family: var(--font-display);
  font-size: clamp(40px, 8vw, 64px);
  line-height: 1.02;
  letter-spacing: 0.01em;
}

.headline-line {
  display: block;
}

.subhead {
  margin: 18px 0 0;
  font-size: 17px;
  line-height: 1.75;
  color: #6d5b56;
}

.hero-intro {
  max-width: 32em;
  margin: 14px 0 0;
  font-size: 15px;
  line-height: 1.85;
  color: #876b60;
}

.hero-stage {
  position: relative;
  width: min(82vw, 380px);
  height: min(42vw, 174px);
  margin: 18px auto 18px;
}

.hero-stage::before {
  content: '';
  position: absolute;
  inset: 10px 0 22px;
  border-radius: 50%;
  border: 1px dashed rgba(111, 82, 66, 0.16);
  background:
    radial-gradient(circle at center, rgba(255, 255, 255, 0.34), transparent 60%),
    radial-gradient(circle at 50% 50%, rgba(255, 228, 213, 0.18), transparent 72%);
  transform: rotate(-18deg) scaleX(1.04) scaleY(0.82);
  transform-origin: center;
}

.center-orb {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 118px;
  height: 118px;
  margin-left: -59px;
  margin-top: -39px;
  border-radius: 50%;
  background: linear-gradient(180deg, #2f2a47 0%, #4b4266 100%);
  box-shadow: 0 18px 40px rgba(69, 56, 95, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
}

.orb-text {
  color: #fff6ec;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.2em;
}

.orbit-chip {
  position: absolute;
  min-width: 60px;
  padding: 7px 9px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(8px);
  box-shadow:
    0 12px 24px rgba(87, 58, 37, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.56);
  text-align: center;
}

.orbit-chip-code {
  color: #614536;
  font-size: 10px;
  font-weight: 700;
}

.hero-actions {
  display: flex;
  justify-content: center;
  margin-top: 146px;
}

.hero-action-btn {
  min-width: min(100%, 280px);
  height: 56px;
  padding: 0 28px;
  border-radius: 999px;
  border: none;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.04em;
  transition:
    transform 0.25s ease,
    box-shadow 0.25s ease,
    filter 0.25s ease;
  cursor: pointer;
}

.primary-btn {
  background: linear-gradient(135deg, #2f2a47 0%, #5b4c88 55%, #7b5f83 100%);
  color: #fff9f0;
  box-shadow: 0 20px 36px rgba(77, 62, 109, 0.26);
}

.hero-action-btn:hover {
  transform: translateY(-2px);
  filter: saturate(1.06);
}

@media (max-width: 380px) {
  .hero {
    padding-left: 18px;
    padding-right: 18px;
  }

  .hero-action-btn {
    width: 100%;
  }
}
</style>
