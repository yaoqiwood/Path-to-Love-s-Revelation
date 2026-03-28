<!-- 主应用组件 -->
<template>
  <el-config-provider :locale="zhCn">
    <!-- 未登录状态：直接显示路由内容 -->
    <router-view v-if="!userStore.isLoggedIn || isAuthPage" />

    <!-- 已登录状态：显示带布局的内容 -->
    <el-container v-else class="app-container">
      <AppHeader :collapsed="sidebarCollapsed" @toggle-sidebar="toggleSidebar" />

      <el-container class="main-container">
        <AppSidebar :collapsed="sidebarCollapsed" @create-project="handleCreateProject" />

        <el-main class="app-main">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>

    <!-- 全局加载 -->
    <LoadingSpinner v-if="globalLoading" fullscreen overlay text="加载中..." />
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import AppHeader from '@/components/common/AppHeader.vue'
import AppSidebar from '@/components/common/AppSidebar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const sidebarCollapsed = ref(false)
const globalLoading = ref(false)

// 判断是否是认证页面
const isAuthPage = computed(() => {
  return ['/login', '/register'].includes(route.path)
})

// 方法
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function handleCreateProject() {
  router.push({ name: 'Projects', query: { create: '1' } })
}

// 初始化
onMounted(async () => {
  globalLoading.value = true
  // await Promise.all([
  //   userStore.init()
  // ])
  globalLoading.value = false
})
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  height: 100%;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --primary-color: #667eea;
  --secondary-color: #764ba2;
}

/* Element Plus 主题覆盖 */
.el-button--primary {
  --el-button-bg-color: #667eea;
  --el-button-border-color: #667eea;
  --el-button-hover-bg-color: #5a6fd6;
  --el-button-hover-border-color: #5a6fd6;
}
</style>

<style scoped>
.app-container {
  height: 100vh;
  flex-direction: column;
}

.main-container {
  flex: 1;
  overflow: hidden;
}

.app-main {
  background: #f5f7fa;
  overflow-y: auto;
  padding: 0;
  position: relative;
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
