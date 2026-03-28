<template>
  <div class="app-shell">
    <div class="app-backdrop app-backdrop-left"></div>
    <div class="app-backdrop app-backdrop-right"></div>

    <main class="phone-shell">
      <RouterView />
    </main>

    <div class="toast-stack">
      <transition-group name="toast-fade" tag="div">
        <div
          v-for="toast in uiState.toasts"
          :key="toast.id"
          class="toast-card"
          :class="`toast-${toast.icon}`"
        >
          {{ toast.title }}
        </div>
      </transition-group>
    </div>

    <div v-if="uiState.loading" class="overlay-mask">
      <div class="overlay-card">
        <div class="overlay-spinner"></div>
        <p class="overlay-text">{{ uiState.loadingText }}</p>
      </div>
    </div>

    <div v-if="uiState.modal" class="overlay-mask">
      <div class="modal-card">
        <h2 class="modal-title">{{ uiState.modal.title || '提示' }}</h2>
        <p class="modal-content">{{ uiState.modal.content || '' }}</p>
        <div class="modal-actions">
          <button
            v-if="uiState.modal.showCancel !== false"
            class="modal-btn modal-btn-ghost"
            type="button"
            @click="handleModalAction(false)"
          >
            {{ uiState.modal.cancelText || '取消' }}
          </button>
          <button
            class="modal-btn modal-btn-primary"
            type="button"
            @click="handleModalAction(true)"
          >
            {{ uiState.modal.confirmText || '确认' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'

import { resolveModalAction, uiState } from '@/platform/ui-state'

function handleModalAction(confirm) {
  resolveModalAction(confirm)
}
</script>

<style lang="less">
.app-shell {
  position: relative;
  min-height: 100vh;
  padding: 18px 14px 22px;
  background:
    radial-gradient(circle at 10% 0%, rgba(255, 199, 173, 0.65), transparent 28%),
    radial-gradient(circle at 100% 14%, rgba(177, 223, 255, 0.55), transparent 22%),
    linear-gradient(180deg, #fffaf4 0%, #fff3ea 48%, #fff9f5 100%);
  overflow-x: hidden;
}

.app-backdrop {
  position: fixed;
  inset: auto;
  border-radius: 999px;
  filter: blur(14px);
  opacity: 0.54;
  pointer-events: none;
}

.app-backdrop-left {
  top: -48px;
  left: -56px;
  width: 180px;
  height: 180px;
  background: linear-gradient(180deg, rgba(255, 173, 136, 0.78) 0%, rgba(255, 139, 126, 0.35) 100%);
}

.app-backdrop-right {
  top: 160px;
  right: -44px;
  width: 160px;
  height: 160px;
  background: linear-gradient(180deg, rgba(139, 200, 255, 0.72) 0%, rgba(121, 129, 255, 0.3) 100%);
}

.phone-shell {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 430px;
  min-height: calc(100vh - 40px);
  margin: 0 auto;
  border-radius: 36px;
  overflow: clip;
  background: rgba(255, 255, 255, 0.74);
  box-shadow:
    0 28px 60px rgba(80, 54, 35, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(20px);
}

.toast-stack {
  position: fixed;
  left: 50%;
  bottom: 24px;
  z-index: 50;
  width: min(100%, 420px);
  padding: 0 18px;
  transform: translateX(-50%);
  pointer-events: none;
}

.toast-card {
  margin-top: 12px;
  padding: 14px 18px;
  border-radius: 18px;
  background: rgba(40, 32, 28, 0.9);
  color: #fffaf5;
  font-size: 14px;
  line-height: 1.5;
  box-shadow: 0 18px 36px rgba(35, 25, 20, 0.22);
}

.overlay-mask {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(39, 28, 24, 0.35);
  backdrop-filter: blur(10px);
}

.overlay-card,
.modal-card {
  width: min(100%, 360px);
  padding: 24px 22px;
  border-radius: 26px;
  background: linear-gradient(180deg, #fffdf9 0%, #fff5ec 100%);
  box-shadow: 0 24px 52px rgba(70, 47, 36, 0.18);
}

.overlay-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.overlay-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(89, 74, 131, 0.16);
  border-top-color: #594a83;
  border-radius: 999px;
  animation: spin 0.8s linear infinite;
}

.overlay-text,
.modal-content {
  margin: 0;
  color: #5d4b43;
  font-size: 15px;
  line-height: 1.7;
  text-align: center;
}

.modal-title {
  margin: 0;
  color: #2f211d;
  font-family: var(--font-display);
  font-size: 26px;
  line-height: 1.2;
  text-align: center;
}

.modal-content {
  margin-top: 14px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 22px;
}

.modal-btn {
  flex: 1;
}

.modal-btn-ghost {
  background: rgba(255, 255, 255, 0.72);
  color: #4d3f39;
}

.modal-btn-primary {
  color: #fffaf5;
  background: linear-gradient(90deg, #2f2a47 0%, #594a83 100%);
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.24s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 480px) {
  .app-shell {
    padding: 0;
  }

  .phone-shell {
    max-width: none;
    min-height: 100vh;
    border-radius: 0;
  }
}
</style>
