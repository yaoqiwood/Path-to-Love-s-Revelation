<!-- 应用头部组件 -->
<template>
  <el-header class="app-header">
    <div class="header-left">
      <el-icon class="menu-toggle" @click="toggleSidebar">
        <Fold v-if="!collapsed" />
        <Expand v-else />
      </el-icon>
      <h1 class="app-title">In Grace</h1>
    </div>


    <div class="header-right">
      <!-- 通知 -->
      <el-badge :value="notificationCount" :hidden="!notificationCount">
        <el-button :icon="Bell" circle />
      </el-badge>

      <!-- 用户菜单 -->
      <el-dropdown trigger="click" @command="handleUserCommand">
        <div class="user-info">
          <el-avatar :size="32" :src="userStore.user?.avatar || defaultAvatar">
            {{ userStore.user?.username?.charAt(0).toUpperCase() }}
          </el-avatar>
          <span class="username">{{ userStore.user?.username }}</span>
          <el-icon>
            <ArrowDown />
          </el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon>
                <User />
              </el-icon>
              个人资料
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon>
                <Setting />
              </el-icon>
              设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon>
                <SwitchButton />
              </el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import {
  Fold,
  Expand,
  Bell,
  ArrowDown,
  User,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'
import defaultAvatar from '@/assets/head-img.jpg'

// Props
interface Props {
  collapsed?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  collapsed: false
})

// Emits
const emit = defineEmits<{
  (e: 'toggle-sidebar'): void
}>()

// Store
const userStore = useUserStore()
const router = useRouter()

// 状态
const notificationCount = ref(0)

// 方法
function toggleSidebar() {
  emit('toggle-sidebar')
}

function handleUserCommand(command: string) {
  switch (command) {
    case 'profile':
      router.push({ name: 'Settings', query: { tab: 'profile' } })
      break
    case 'settings':
      router.push({ name: 'Settings' })
      break
    case 'logout':
      userStore.logout()
      window.location.href = '/login'
      break
  }
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-toggle {
  font-size: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.menu-toggle:hover {
  transform: scale(1.1);
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  background: linear-gradient(90deg, #fff, #e0e0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}


.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 20px;
  transition: background 0.3s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}

.username {
  font-size: 14px;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
