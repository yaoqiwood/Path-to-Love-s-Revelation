import path from 'node:path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

function formatVw(value) {
  const nextValue = Number(value) / 7.5
  const fixedValue = nextValue.toFixed(6)
  return `${fixedValue.replace(/\.?0+$/, '')}vw`
}

function rpxToVwPlugin() {
  return {
    postcssPlugin: 'codex-rpx-to-vw',
    Declaration(declaration) {
      if (!declaration.value || !declaration.value.includes('rpx')) {
        return
      }

      declaration.value = declaration.value.replace(
        /(-?\d*\.?\d+)rpx/g,
        (_, value) => formatVw(value)
      )
    }
  }
}

rpxToVwPlugin.postcss = true

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@dcloudio/uni-app': path.resolve(__dirname, 'src/platform/uni-app-shim.js')
    }
  },
  define: {
    uni: 'globalThis.__APP_UNI__',
    uniCloud: 'globalThis.__APP_UNICLOUD__',
    getCurrentPages: 'globalThis.__APP_GET_CURRENT_PAGES__'
  },
  css: {
    postcss: {
      plugins: [rpxToVwPlugin()]
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8081',
        changeOrigin: true
      }
    }
  }
})
