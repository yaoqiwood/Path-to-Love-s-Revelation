<!-- 仪表盘页面 -->
<template>
  <div class="dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1>欢迎回来，{{ userStore.user?.nickname || userStore.user?.username }}！</h1>
        <p>今天是 {{ currentDate }}，开始您的工作吧！</p>
      </div>
      <div class="quick-actions">
        <el-button type="primary" :icon="Setting" @click="goToSettings">
          系统设置
        </el-button>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.title">
        <div class="stat-icon" :style="{ background: stat.color }">
          <el-icon><component :is="stat.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-title">{{ stat.title }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { 
  User,
  Setting,
  Connection,
  Document
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 当前日期
const currentDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    weekday: 'long'
  })
})

// 统计数据
const stats = ref([
  { title: '平台用户', value: '12', icon: markRaw(User), color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { title: '系统配置', value: '45', icon: markRaw(Setting), color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { title: '接口请求', value: '28K', icon: markRaw(Connection), color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  { title: '操作日志', value: '8K', icon: markRaw(Document), color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }
])

function goToSettings() {
  router.push({ name: 'Settings' })
}
</script>

<style scoped>
.dashboard {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100%;
}

.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  margin-bottom: 24px;
}

.welcome-content h1 {
  font-size: 24px;
  margin: 0 0 8px;
}

.welcome-content p {
  margin: 0;
  opacity: 0.9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 22px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
}

.stat-title {
  font-size: 13px;
  color: #666;
}
</style>
