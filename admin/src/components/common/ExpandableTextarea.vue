<template>
  <div class="expandable-textarea" ref="wrapperRef">
    <!-- 普通模式 textarea -->
    <div class="expandable-textarea__wrapper">
      <textarea ref="textareaRef" :value="modelValue" @input="handleInput" :placeholder="placeholder" :rows="rows"
        :disabled="disabled" class="expandable-textarea__input"></textarea>
      <button v-if="!disabled" class="expandable-textarea__expand-btn" @click="openExpand" title="展开编辑">
        <el-icon :size="14">
          <FullScreen />
        </el-icon>
      </button>
    </div>

    <!-- 展开浮层：定位在原始 textarea 位置，向下展开 -->
    <Teleport to="body">
      <div v-if="expanded" class="expandable-textarea__backdrop" @click="closeExpand"></div>
      <div v-if="expanded" ref="panelRef" class="expandable-textarea__panel" :style="panelStyle">
        <textarea ref="expandTextareaRef" :value="modelValue" @input="handleInput" :placeholder="placeholder"
          class="expandable-textarea__panel-input"></textarea>
        <div class="expandable-textarea__panel-footer">
          <span class="expandable-textarea__char-count">{{ (modelValue || '').length }} 字</span>
          <button class="expandable-textarea__collapse-btn" @click="closeExpand" title="收起">
            <el-icon :size="12">
              <ArrowUp />
            </el-icon>
            <span>收起</span>
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onBeforeUnmount } from 'vue'
import { FullScreen, ArrowUp } from '@element-plus/icons-vue'

interface Props {
  modelValue: string
  placeholder?: string
  rows?: number
  disabled?: boolean
  /** 展开后底部距视口底部的百分比，默认 0.15 即到 85% 处 */
  expandRatio?: number
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '',
  rows: 3,
  disabled: false,
  expandRatio: 0.08,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const wrapperRef = ref<HTMLElement>()
const textareaRef = ref<HTMLTextAreaElement>()
const expandTextareaRef = ref<HTMLTextAreaElement>()
const panelRef = ref<HTMLElement>()
const expanded = ref(false)

const panelStyle = reactive({
  top: '0px',
  left: '0px',
  width: '0px',
  '--start-height': '0px',
  '--end-height': '0px',
})

function handleInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}

function openExpand() {
  const rect = wrapperRef.value?.getBoundingClientRect()
  if (!rect) return

  const startH = rect.height
  const viewportH = window.innerHeight
  const endH = viewportH * (1 - props.expandRatio) - rect.top

  panelStyle.top = `${rect.top}px`
  panelStyle.left = `${rect.left}px`
  panelStyle.width = `${rect.width}px`
  panelStyle['--start-height'] = `${startH}px`
  panelStyle['--end-height'] = `${Math.max(endH, startH + 100)}px`

  expanded.value = true

  nextTick(() => {
    expandTextareaRef.value?.focus()
    const len = expandTextareaRef.value?.value.length || 0
    expandTextareaRef.value?.setSelectionRange(len, len)
  })
}

function closeExpand() {
  // 触发收起动画
  panelRef.value?.classList.add('collapsing')
  setTimeout(() => {
    expanded.value = false
    nextTick(() => textareaRef.value?.focus())
  }, 200)
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && expanded.value) {
    closeExpand()
  }
}

// 全局 ESC 监听
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', handleKeydown)
}
onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})

defineExpose({ focus: () => textareaRef.value?.focus() })
</script>

<style scoped>
.expandable-textarea__wrapper {
  position: relative;
}

.expandable-textarea__input {
  width: 100%;
  border: 1px solid #e5e6eb;
  border-radius: 8px;
  padding: 10px 36px 10px 12px;
  font-size: 16px;
  line-height: 1.5;
  resize: vertical;
  outline: none;
  font-family: inherit;
  color: #1d2129;
  transition: border-color 0.2s;
  min-height: 60px;
  box-sizing: border-box;
}

.expandable-textarea__input:focus {
  border-color: #4080ff;
}

.expandable-textarea__expand-btn {
  position: absolute;
  top: 6px;
  right: 20px;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 4px;
  cursor: pointer;
  color: #8c8c8c;
  transition: all 0.2s;
}

.expandable-textarea__expand-btn:hover {
  background: rgba(64, 128, 255, 0.1);
  color: #4080ff;
}

/* ===== 遮罩 ===== */
.expandable-textarea__backdrop {
  position: fixed;
  inset: 0;
  z-index: 9998;
  background: rgba(0, 0, 0, 0.18);
  animation: fade-in 0.2s ease;
}

/* ===== 展开浮层 ===== */
.expandable-textarea__panel {
  position: fixed;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #d4d7de;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  overflow: hidden;

  /* 从原始高度动画到目标高度 */
  animation: expand-down 0.3s cubic-bezier(0.25, 1, 0.5, 1) forwards;
}

.expandable-textarea__panel.collapsing {
  animation: collapse-up 0.2s ease-in forwards;
}

.expandable-textarea__panel-input {
  flex: 1;
  width: 100%;
  border: none;
  outline: none;
  padding: 12px 14px;
  font-size: 16px;
  line-height: 1.6;
  resize: none;
  font-family: inherit;
  color: #1d2129;
  box-sizing: border-box;
}

.expandable-textarea__panel-input::placeholder {
  color: #c0c4cc;
}

.expandable-textarea__panel-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 14px;
  border-top: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.expandable-textarea__char-count {
  font-size: 12px;
  color: #909399;
}

.expandable-textarea__collapse-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border: none;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 4px;
  cursor: pointer;
  color: #606266;
  font-size: 12px;
  transition: all 0.2s;
}

.expandable-textarea__collapse-btn:hover {
  background: rgba(64, 128, 255, 0.1);
  color: #4080ff;
}

/* ===== 动画 ===== */
@keyframes expand-down {
  from {
    height: var(--start-height);
    opacity: 0.8;
  }

  to {
    height: var(--end-height);
    opacity: 1;
  }
}

@keyframes collapse-up {
  from {
    height: var(--end-height);
    opacity: 1;
  }

  to {
    height: var(--start-height);
    opacity: 0;
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}
</style>
