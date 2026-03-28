<!-- 应用侧边栏组件 -->
<template>
  <el-aside :width="collapsed ? '64px' : '220px'" class="app-sidebar">
    <el-menu :default-active="activeMenu" :collapse="collapsed" :collapse-transition="false" router
      class="sidebar-menu">

      <!-- 动态菜单 -->
      <sidebar-item v-for="route in userStore.menus" :key="route.path" :item="route" :base-path="route.path" />

    </el-menu>

    <!-- 快速创建按钮 -->
    <div class="quick-create" v-if="!collapsed">
      <el-button type="primary" class="create-btn" @click="showCreateDialog">
        <el-icon>
          <Plus />
        </el-icon>
        新建项目
      </el-button>
    </div>
    <div class="quick-create collapsed" v-else>
      <el-button type="primary" circle :icon="Plus" @click="showCreateDialog" />
    </div>
  </el-aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/store/user' // Import user store
import SidebarItem from './SidebarItem.vue' // Import SidebarItem

import {
  Plus
} from '@element-plus/icons-vue'

// Props
interface Props {
  collapsed?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  collapsed: false
})

// Emits
const emit = defineEmits<{
  (e: 'create-project'): void
}>()

// Route
const route = useRoute()
const userStore = useUserStore() // Use user store

// 计算当前激活的菜单项
const activeMenu = computed(() => route.path)

// 方法
function showCreateDialog() {
  emit('create-project')
}
</script>

<style scoped>
.app-sidebar {
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid #e8e8e8;
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  overflow-x: hidden;
  overflow-y: auto;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 100%;
}

.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  height: 50px;
  line-height: 50px;
  transition: all 0.3s;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-sub-menu__title:hover {
  background: linear-gradient(90deg, #f0f5ff, #fff);
}

.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(90deg, #e6f4ff, #fff);
  border-right: 3px solid #667eea;
  color: #667eea;
}

.sidebar-menu .el-menu-item .el-icon,
.sidebar-menu .el-sub-menu__title .el-icon {
  font-size: 18px;
}

.menu-divider {
  height: 1px;
  background: #e8e8e8;
  margin: 16px 20px;
}

.quick-create {
  padding: 16px;
  border-top: 1px solid #e8e8e8;
}

.quick-create.collapsed {
  padding: 16px 12px;
  display: flex;
  justify-content: center;
}

.create-btn {
  width: 100%;
  height: 40px;
  border-radius: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-weight: 500;
}

.create-btn:hover {
  background: linear-gradient(135deg, #5a6fd6 0%, #6a4190 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}
</style>
