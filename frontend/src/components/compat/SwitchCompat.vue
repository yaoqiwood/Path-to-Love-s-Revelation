<template>
  <label class="switch-compat" :style="{ '--switch-color': color || '#1f6b52' }">
    <input class="switch-input" type="checkbox" :checked="checked" @change="handleChange" />
    <span class="switch-track"></span>
  </label>
</template>

<script setup>
const emit = defineEmits(['change'])
defineProps({
  checked: {
    type: Boolean,
    default: false
  },
  color: {
    type: String,
    default: '#1f6b52'
  }
})

function handleChange(event) {
  emit('change', {
    detail: {
      value: event.target.checked
    }
  })
}
</script>

<style lang="less" scoped>
.switch-compat {
  position: relative;
  display: inline-flex;
  width: 48px;
  height: 28px;
}

.switch-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  margin: 0;
}

.switch-track {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 999px;
  background: rgba(94, 68, 54, 0.2);
  transition: background 0.2s ease;
}

.switch-track::after {
  content: '';
  position: absolute;
  left: 3px;
  top: 3px;
  width: 22px;
  height: 22px;
  border-radius: 999px;
  background: #ffffff;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.14);
  transition: transform 0.2s ease;
}

.switch-input:checked + .switch-track {
  background: var(--switch-color);
}

.switch-input:checked + .switch-track::after {
  transform: translateX(20px);
}
</style>
