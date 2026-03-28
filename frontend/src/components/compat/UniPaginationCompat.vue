<template>
  <div class="pagination-compat">
    <button
      class="pagination-btn"
      type="button"
      :disabled="currentPage <= 1"
      @click="changePage(currentPage - 1)"
    >
      上一页
    </button>
    <span class="pagination-text">第 {{ currentPage }} / {{ totalPages }} 页</span>
    <button
      class="pagination-btn"
      type="button"
      :disabled="currentPage >= totalPages"
      @click="changePage(currentPage + 1)"
    >
      下一页
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const emit = defineEmits(['change'])
const props = defineProps({
  current: {
    type: [Number, String],
    default: 1
  },
  pageSize: {
    type: [Number, String],
    default: 10
  },
  total: {
    type: [Number, String],
    default: 0
  }
})

const currentPage = computed(() => Math.max(1, Number(props.current) || 1))
const totalPages = computed(() => {
  const total = Math.max(0, Number(props.total) || 0)
  const pageSize = Math.max(1, Number(props.pageSize) || 10)
  return Math.max(1, Math.ceil(total / pageSize))
})

function changePage(page) {
  const nextPage = Math.min(totalPages.value, Math.max(1, page))
  emit('change', {
    current: nextPage
  })
}
</script>

<style lang="less" scoped>
.pagination-compat {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.pagination-btn {
  min-width: 88px;
  padding: 10px 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  color: #4d3f39;
  border: 1px solid rgba(94, 68, 54, 0.12);
}

.pagination-btn:disabled {
  opacity: 0.42;
  cursor: not-allowed;
}

.pagination-text {
  font-size: 14px;
  color: #6d5b56;
}
</style>
