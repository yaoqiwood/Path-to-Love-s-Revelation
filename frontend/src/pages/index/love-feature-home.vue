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
        <div class="profile-pill">
          <span class="profile-label">状态</span>
          <strong>{{ mbtiStatus }}</strong>
        </div>
      </section>

      <section class="feature-grid">
        <article class="feature-card feature-card-primary">
          <p class="card-kicker">MODULE 01</p>
          <h2 class="card-title">MBTI 测试</h2>
          <p class="card-copy">重新进入测试流程，查看你在关系里的节奏、偏好与吸引方向。</p>
          <button class="card-btn card-btn-primary" type="button" @click="goMbtiTest">
            开始测试
          </button>
        </article>

        <article class="feature-card">
          <p class="card-kicker">MODULE 02</p>
          <h2 class="card-title">信号小屋</h2>
          <p class="card-copy">进入聊天功能的信号小屋，查看消息、开启对话，慢慢靠近你想认识的人。</p>
          <button class="card-btn" type="button" @click="goSignalCabin">
            进入小屋
          </button>
        </article>

        <article class="feature-card feature-card-accent">
          <p class="card-kicker">MODULE 03</p>
          <h2 class="card-title">心动坐标</h2>
          <p class="card-copy">
            男生和女生分别从 24 位异性里选出自己最想了解的 10 个人，并完成一份带顺序的心动排序。
          </p>
          <button class="card-btn" type="button" @click="goHeartCoordinate">
            查看入口
          </button>
        </article>
      </section>
    </section>
  </section>
</template>

<script setup>
import { computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { app } from '@/platform/app-bridge'

const PROFILE_KEY = 'mbtiPersonnelProfile'

const router = useRouter()
const profile = reactive(getStoredProfile())

const displayName = computed(() => profile.nickname || profile.name || '爱的来宾')
const mbtiStatus = computed(() => (String(profile.mbti || '').trim() ? profile.mbti : '未完成测试'))

function getStoredProfile() {
  try {
    const storedProfile = app.getStorageSync(PROFILE_KEY)
    return storedProfile && typeof storedProfile === 'object' ? storedProfile : {}
  } catch (error) {
    return {}
  }
}

function goMbtiTest() {
  const query = []
  if (profile.name) {
    query.push(`name=${encodeURIComponent(profile.name)}`)
  }
  if (profile.personnel_id || profile.id) {
    query.push(`personnelId=${encodeURIComponent(profile.personnel_id || profile.id)}`)
  }
  if (profile.wechat_id || profile.wx_openid) {
    query.push(`wxOpenid=${encodeURIComponent(profile.wechat_id || profile.wx_openid)}`)
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
  padding: calc(44px + var(--safe-top, 0px)) clamp(22px, 5vw, 54px) calc(40px + var(--safe-bottom, 0px));
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
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 28px;
}

.profile-pill {
  padding: 16px 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 18px 30px rgba(117, 88, 63, 0.08);
  backdrop-filter: blur(12px);
}

.profile-label {
  display: block;
  color: #92756a;
  font-size: 12px;
  letter-spacing: 0.08em;
}

.profile-pill strong {
  display: block;
  margin-top: 8px;
  color: #322521;
  font-size: 20px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: 26px;
}

.feature-card {
  min-height: 290px;
  padding: 24px 22px;
  border-radius: 30px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.88), rgba(255, 248, 242, 0.72)),
    linear-gradient(135deg, rgba(255, 240, 229, 0.76), rgba(255, 255, 255, 0.5));
  box-shadow: 0 24px 42px rgba(117, 88, 63, 0.1);
  display: flex;
  flex-direction: column;
}

.feature-card-primary {
  background:
    linear-gradient(180deg, rgba(48, 42, 72, 0.95), rgba(84, 70, 126, 0.92)),
    linear-gradient(145deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.02));
}

.feature-card-accent {
  background:
    linear-gradient(180deg, rgba(255, 248, 241, 0.92), rgba(255, 239, 230, 0.84)),
    radial-gradient(circle at top right, rgba(255, 189, 156, 0.3), transparent 44%);
}

.card-kicker {
  margin: 0;
  color: rgba(111, 92, 84, 0.82);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.18em;
}

.feature-card-primary .card-kicker,
.feature-card-primary .card-title,
.feature-card-primary .card-copy {
  color: #fff7ef;
}

.card-title {
  margin: 16px 0 0;
  color: #2f231f;
  font-size: 32px;
  line-height: 1.08;
}

.card-copy {
  margin: 14px 0 0;
  color: #6d5d57;
  font-size: 15px;
  line-height: 1.9;
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

@media (max-width: 960px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }

  .feature-card {
    min-height: 248px;
  }
}

@media (max-width: 640px) {
  .feature-shell {
    padding-left: 18px;
    padding-right: 18px;
  }

  .profile-strip {
    grid-template-columns: 1fr;
  }
}
</style>
