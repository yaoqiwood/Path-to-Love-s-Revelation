<template>
  <div
    ref="root"
    v-bind="$attrs"
    class="scroll-view-compat"
    :class="{
      'scroll-x': scrollX,
      'scroll-y': scrollY
    }"
    @scroll="handleScroll"
  >
    <slot />
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'

const emit = defineEmits(['scroll'])
const props = defineProps({
  scrollX: {
    type: Boolean,
    default: false
  },
  scrollY: {
    type: Boolean,
    default: false
  },
  scrollTop: {
    type: [Number, String],
    default: 0
  },
  scrollLeft: {
    type: [Number, String],
    default: 0
  },
  scrollIntoView: {
    type: String,
    default: ''
  },
  scrollWithAnimation: {
    type: Boolean,
    default: false
  }
})

const root = ref(null)

function syncScrollPosition() {
  if (!root.value) {
    return
  }

  root.value.scrollTop = Number(props.scrollTop) || 0
  root.value.scrollLeft = Number(props.scrollLeft) || 0
}

function syncScrollIntoView() {
  if (!root.value || !props.scrollIntoView) {
    return
  }

  const target = root.value.querySelector(`#${CSS.escape(props.scrollIntoView)}`)
  if (!target) {
    return
  }

  target.scrollIntoView({
    block: 'nearest',
    behavior: props.scrollWithAnimation ? 'smooth' : 'auto'
  })
}

function handleScroll(event) {
  emit('scroll', {
    detail: {
      scrollTop: event.target.scrollTop,
      scrollLeft: event.target.scrollLeft
    }
  })
}

watch(
  () => [props.scrollTop, props.scrollLeft],
  () => {
    nextTick(syncScrollPosition)
  }
)

watch(
  () => props.scrollIntoView,
  () => {
    nextTick(syncScrollIntoView)
  }
)

onMounted(() => {
  syncScrollPosition()
  syncScrollIntoView()
})
</script>

<style lang="less" scoped>
.scroll-view-compat {
  min-width: 0;
}

.scroll-x {
  overflow-x: auto;
  overflow-y: hidden;
}

.scroll-y {
  overflow-y: auto;
  overflow-x: hidden;
}
</style>
