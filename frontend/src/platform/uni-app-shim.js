import { onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

export function onLoad(callback) {
  const route = useRoute()
  onMounted(() => {
    callback(route.query || {})
  })
}

export function onUnload(callback) {
  onUnmounted(() => {
    callback()
  })
}
