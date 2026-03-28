<template>
  <label class="picker-compat">
    <slot />
    <select class="picker-native" :value="normalizedValue" @change="handleChange">
      <option v-for="(item, index) in range" :key="`${item}-${index}`" :value="index">
        {{ item }}
      </option>
    </select>
  </label>
</template>

<script setup>
import { computed } from 'vue'

const emit = defineEmits(['change'])
const props = defineProps({
  range: {
    type: Array,
    default: () => []
  },
  value: {
    type: [Number, String],
    default: 0
  }
})

const normalizedValue = computed(() => Number(props.value) || 0)

function handleChange(event) {
  emit('change', {
    detail: {
      value: Number(event.target.value) || 0
    }
  })
}
</script>

<style lang="less" scoped>
.picker-compat {
  position: relative;
  display: block;
}

.picker-native {
  position: absolute;
  inset: 0;
  width: 100%;
  opacity: 0;
  cursor: pointer;
}
</style>
