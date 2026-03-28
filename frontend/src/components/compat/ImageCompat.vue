<template>
  <img
    v-bind="$attrs"
    :src="src || undefined"
    :alt="alt"
    :style="{
      objectFit: fitMode
    }"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  src: {
    type: String,
    default: ''
  },
  alt: {
    type: String,
    default: ''
  },
  mode: {
    type: String,
    default: 'fill'
  }
})

const fitMode = computed(() => {
  if (props.mode === 'aspectFit') {
    return 'contain'
  }
  if (props.mode === 'aspectFill') {
    return 'cover'
  }
  return 'fill'
})
</script>
