<template>
  <section class="welcome-page">
    <section class="hero">
      <div class="hero-backdrop hero-backdrop-left"></div>
      <div class="hero-backdrop hero-backdrop-right"></div>

      <div class="hero-copy">
        <p class="eyebrow">PATH TO LOVE</p>
        <h1 class="headline">欢迎来到“爱的启示路”</h1>
        <p class="subhead">先看见自己，再靠近彼此。</p>
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
        <button class="hero-action-btn primary-btn" type="button" @click="enterAsGuest">
          开始浏览
        </button>
        <button class="hero-action-btn ghost-btn" type="button" @click="enterAsParticipant">
          进入测试
        </button>
      </div>
    </section>

    <section class="summary-panel">
      <article class="summary-card">
        <span class="summary-label">模拟参与者</span>
        <strong class="summary-value">{{ overview.participants }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">后台账号</span>
        <strong class="summary-value">{{ overview.users + overview.admins }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">已审核资料</span>
        <strong class="summary-value">{{ overview.approved }}</strong>
      </article>
    </section>

    <section class="entry-grid">
      <button class="entry-card" type="button" @click="enterAsGuest">
        <span class="entry-tag">访客</span>
        <strong class="entry-title">欢迎页</strong>
        <span class="entry-desc">先逛一圈</span>
      </button>

      <button class="entry-card" type="button" @click="enterAsParticipant">
        <span class="entry-tag">测试</span>
        <strong class="entry-title">MBTI</strong>
        <span class="entry-desc">直接开答</span>
      </button>

      <button class="entry-card accent-card" type="button" @click="enterAsAdmin">
        <span class="entry-tag">后台</span>
        <strong class="entry-title">Mock 管理</strong>
        <span class="entry-desc">查看数据</span>
      </button>
    </section>

    <section class="persona-grid">
      <article v-for="item in showcaseList" :key="item.code" class="persona-card">
        <div class="persona-top">
          <div class="avatar-shell">
            <img class="persona-avatar" :src="item.avatar" :alt="item.name" />
          </div>
          <span class="persona-code">{{ item.code }}</span>
        </div>
        <h3 class="persona-name">{{ item.name }}</h3>
        <p class="persona-note">{{ item.note }}</p>
      </article>
    </section>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { applyMockPreset, getMockOverview } from '@/platform/mock-presets'

const router = useRouter()

const orbitTypes = [
  { code: 'INFP' },
  { code: 'ENFP' },
  { code: 'INFJ' },
  { code: 'ENFJ' },
  { code: 'INTJ' },
  { code: 'ESFP' },
  { code: 'ISFP' },
  { code: 'ENTP' }
]

const showcaseList = computed(() => [
  {
    code: 'INFP',
    name: '月光理想家',
    note: '细腻温柔',
    avatar: '/static/mbti-personas/infp.svg'
  },
  {
    code: 'ENFP',
    name: '烟火冒险家',
    note: '热烈灵动',
    avatar: '/static/mbti-personas/enfp.svg'
  },
  {
    code: 'INFJ',
    name: '静谧预言家',
    note: '深情克制',
    avatar: '/static/mbti-personas/infj.svg'
  },
  {
    code: 'ENFJ',
    name: '暖场指挥家',
    note: '温暖有力',
    avatar: '/static/mbti-personas/enfj.svg'
  }
])

const overview = getMockOverview()

function orbitStyle(index) {
  const positions = [
    { top: '18px', left: '118px' },
    { top: '62px', right: '16px' },
    { top: '152px', right: '-4px' },
    { top: '256px', right: '42px' },
    { top: '308px', left: '128px' },
    { top: '258px', left: '18px' },
    { top: '154px', left: '-6px' },
    { top: '54px', left: '24px' }
  ]

  return positions[index] || {}
}

function enterAsGuest() {
  applyMockPreset('guest')
  router.push('/pages/index/service')
}

function enterAsParticipant() {
  applyMockPreset('participant')
  router.push('/pages/user/helper')
}

function enterAsAdmin() {
  applyMockPreset('admin')
  router.push('/pkg/guide/hub')
}
</script>

<style scoped lang="less">
.welcome-page {
  min-height: 100vh;
  padding: 24px 20px calc(var(--safe-bottom) + 24px);
  background:
    radial-gradient(circle at top left, rgba(255, 194, 159, 0.42), transparent 30%),
    radial-gradient(circle at top right, rgba(135, 202, 255, 0.4), transparent 24%),
    linear-gradient(180deg, #fffdf8 0%, #fff4ec 46%, #fffaf4 100%);
}

.hero {
  position: relative;
  overflow: hidden;
  padding: 24px 4px 10px;
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
.hero-actions,
.summary-panel,
.entry-grid,
.persona-grid {
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
  margin: 12px 0 0;
  color: #2f211d;
  font-family: var(--font-display);
  font-size: clamp(36px, 8vw, 48px);
  line-height: 1.08;
}

.subhead {
  margin: 14px 0 0;
  font-size: 15px;
  line-height: 1.7;
  color: #6d5b56;
}

.hero-stage {
  position: relative;
  width: min(82vw, 340px);
  height: min(82vw, 340px);
  margin: 26px auto 18px;
  border-radius: 50%;
  border: 1px dashed rgba(111, 82, 66, 0.16);
}

.center-orb {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 118px;
  height: 118px;
  margin-left: -59px;
  margin-top: -59px;
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
  min-width: 78px;
  padding: 10px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.76);
  backdrop-filter: blur(8px);
  box-shadow: 0 12px 24px rgba(87, 58, 37, 0.08);
  text-align: center;
}

.orbit-chip-code {
  color: #614536;
  font-size: 12px;
  font-weight: 700;
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.hero-action-btn {
  flex: 1;
  height: 52px;
  border-radius: 999px;
  border: none;
  font-size: 16px;
  font-weight: 600;
}

.primary-btn {
  background: linear-gradient(90deg, #2f2a47 0%, #594a83 100%);
  color: #fff9f0;
  box-shadow: 0 18px 32px rgba(77, 62, 109, 0.22);
}

.ghost-btn {
  background: rgba(255, 255, 255, 0.68);
  color: #4e3d37;
  border: 1px solid rgba(94, 68, 54, 0.12);
}

.summary-panel {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 8px;
}

.summary-card,
.entry-card,
.persona-card {
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 18px 34px rgba(117, 88, 63, 0.1);
  backdrop-filter: blur(10px);
}

.summary-card {
  padding: 16px 14px;
}

.summary-label {
  display: block;
  color: #8f776d;
  font-size: 12px;
}

.summary-value {
  display: block;
  margin-top: 8px;
  color: #342925;
  font-size: 22px;
  font-weight: 700;
}

.entry-grid {
  display: grid;
  gap: 14px;
  margin-top: 18px;
}

.entry-card {
  padding: 20px;
  text-align: left;
  border: none;
}

.accent-card {
  background: linear-gradient(135deg, rgba(255, 247, 239, 0.98) 0%, rgba(243, 239, 255, 0.98) 100%);
}

.entry-tag {
  display: block;
  color: #8d5d41;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 12px;
  font-weight: 700;
}

.entry-title {
  display: block;
  margin-top: 10px;
  color: #2f211d;
  font-size: 24px;
  line-height: 1.2;
}

.entry-desc {
  display: block;
  margin-top: 8px;
  color: #6f615c;
  font-size: 14px;
}

.persona-grid {
  margin-top: 18px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.persona-card {
  padding: 18px;
}

.persona-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.avatar-shell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 108px;
  height: 120px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.56);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.35);
}

.persona-avatar {
  width: 90px;
  height: 102px;
  object-fit: contain;
}

.persona-code {
  display: inline-flex;
  align-items: center;
  height: fit-content;
  padding: 8px 12px;
  border-radius: 999px;
  background: #fff1e8;
  color: #8d5d41;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
}

.persona-name {
  margin: 14px 0 0;
  color: #2c211e;
  font-size: 20px;
  line-height: 1.2;
}

.persona-note {
  margin: 8px 0 0;
  color: #634d43;
  font-size: 14px;
}

@media (max-width: 380px) {
  .summary-panel,
  .persona-grid {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    flex-direction: column;
  }
}
</style>
