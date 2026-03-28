<template>
  <template v-if="!item.hidden">
    <template v-if="hasOneShowingChild(item.children, item) && (!onlyOneChild.children || onlyOneChild.noShowingChildren) && !item.alwaysShow">
      <el-menu-item :index="resolvePath(onlyOneChild.paths || onlyOneChild.path)" :class="{'submenu-title-noDropdown':!isNest}">
        <el-icon>
           <component :is="resolveIcon(onlyOneChild) || resolveIcon(item)" />
        </el-icon>
        <template #title>{{ onlyOneChild.menu_name || onlyOneChild.name || onlyOneChild.meta?.title }}</template>
      </el-menu-item>
    </template>

    <el-sub-menu v-else :index="resolvePath(item.paths || item.path)" popper-append-to-body>
      <template #title>
        <el-icon><component :is="resolveIcon(item)" /></el-icon>
        <span>{{ item.menu_name || item.name || item.meta?.title }}</span>
      </template>
      <sidebar-item
        v-for="child in item.children"
        :key="child.paths || child.path"
        :is-nest="true"
        :item="child"
        :base-path="resolvePath(child.paths || child.path)"
      />
    </el-sub-menu>
  </template>
</template>

<script setup lang="ts">
import { ref, markRaw } from 'vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// markRaw 防止 Vue 将图标组件包裹为 reactive proxy（会导致 SVG 渲染失败）
const icons: Record<string, any> = markRaw({ ...ElementPlusIconsVue })

function getIcon(name?: string) {
  if (!name) return null
  return icons[name] || null
}

/** 从 menu item 上解析图标，兼容 menu_icon 和 meta.icon，无配置时返回默认图标 */
function resolveIcon(menuItem: any) {
  if (!menuItem) return icons['Menu']
  const name = menuItem.menu_icon || menuItem.meta?.icon
  return getIcon(name) || icons['Menu']
}

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  isNest: {
    type: Boolean,
    default: false
  },
  basePath: {
    type: String,
    default: ''
  }
})

const onlyOneChild = ref<any>(null)

function hasOneShowingChild(children: any[] = [], parent: any) {
  const showingChildren = children.filter((item: any) => {
    if (item.hidden || item.show_status === 0) {
      return false
    } else {
      onlyOneChild.value = item
      return true
    }
  })

  // When there is only one child router, the child router is displayed by default
  if (showingChildren.length === 1) {
    return true
  }

  // Show parent if there are no child router to display
  if (showingChildren.length === 0) {
    onlyOneChild.value = { ...parent, path: '', noShowingChildren: true }
    return true
  }

  return false
}

function resolvePath(routePath: string) {
    if (isExternal(routePath)) {
        return routePath
    }
    if (isExternal(props.basePath)) {
        return props.basePath
    }
    // Simple path join if not absolute
    if (routePath.startsWith('/')) {
        return routePath
    }
    // If base path is just / and route is foo, return /foo
    // If base path is /foo and route is bar, return /foo/bar
    const base = props.basePath.endsWith('/') ? props.basePath : props.basePath + '/'
    return base + routePath
}

function isExternal(path: string) {
  return /^(https?:|mailto:|tel:)/.test(path)
}
</script>
