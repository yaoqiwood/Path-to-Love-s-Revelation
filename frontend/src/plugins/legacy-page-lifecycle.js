const LOAD_FLAG = Symbol('legacy-page-load-flag')
const LOAD_PATH = Symbol('legacy-page-load-path')

function runHook(instance, hookName, payload) {
  const hook = instance?.$options?.[hookName]
  if (typeof hook === 'function') {
    return hook.call(instance, payload)
  }
  return undefined
}

export default {
  install(app) {
    app.mixin({
      mounted() {
        if (!this.$route) {
          return
        }

        if (!this[LOAD_FLAG]) {
          this[LOAD_FLAG] = true
          this[LOAD_PATH] = this.$route.fullPath
          runHook(this, 'onLoad', this.$route.query || {})
        }
      },
      beforeUnmount() {
        runHook(this, 'onUnload')
      },
      watch: {
        $route(to) {
          if (!to || this[LOAD_PATH] === to.fullPath) {
            return
          }

          this[LOAD_PATH] = to.fullPath
          runHook(this, 'onLoad', to.query || {})
        }
      }
    })
  }
}
