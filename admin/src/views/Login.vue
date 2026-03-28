<!-- 登录页面 -->
<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-left">
        <div class="brand">
          <h1>In Grace</h1>
          <p>活动管理后台</p>
        </div>
        <div class="features">
          <div class="feature-item">
            <el-icon>
              <MagicStick />
            </el-icon>
            <span>性格测试</span>
          </div>
          <div class="feature-item">
            <el-icon>
              <VideoCamera />
            </el-icon>
            <span>智能配对</span>
          </div>
          <div class="feature-item">
            <el-icon>
              <Files />
            </el-icon>
            <span>热火朝天</span>
          </div>
        </div>
      </div>

      <div class="login-right">
        <el-card class="login-card">
          <h2>登录</h2>
          <p class="subtitle">欢迎回来，请登录您的账户</p>

          <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
            <el-form-item prop="username">
              <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" size="large" />
            </el-form-item>

            <el-form-item prop="password">
              <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" size="large"
                show-password />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" native-type="submit" :loading="loading" size="large" class="login-btn">
                登录
              </el-button>
            </el-form-item>
          </el-form>

          <div class="login-footer">
            <span>还没有账户？</span>
            <router-link to="/register">立即注册</router-link>
          </div>

          <div class="token-login-divider">
            <span>或</span>
          </div>

          <el-button type="default" class="token-login-btn" @click="tokenDialogVisible = true">
            🔑 参与者Token登录
          </el-button>
        </el-card>
      </div>
    </div>

    <!-- 参与者Token登录弹窗 -->
    <el-dialog v-model="tokenDialogVisible" title="参与者登录" width="400px" destroy-on-close>
      <el-form @submit.prevent="handleTokenLogin">
        <el-form-item>
          <el-input
            v-model="tokenInput"
            placeholder="请输入永久Token，如 holy-grace-847"
            size="large"
            clearable
            :prefix-icon="Key"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tokenDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="tokenLoading" @click="handleTokenLogin">登录</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { User, Lock, Key, MagicStick, VideoCamera, Files } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

// Token登录
const tokenDialogVisible = ref(false)
const tokenInput = ref('')
const tokenLoading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

async function handleLogin() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    const success = await userStore.login(form)
    loading.value = false

    if (success) {
      ElMessage.success('登录成功')
      const redirect = route.query.redirect as string || '/dashboard'
      router.push(redirect)
    }
  })
}

async function handleTokenLogin() {
  const token = tokenInput.value.trim()
  if (!token) {
    ElMessage.warning('请输入永久Token')
    return
  }
  tokenLoading.value = true
  const success = await userStore.loginByToken(token)
  tokenLoading.value = false
  if (success) {
    tokenDialogVisible.value = false
    ElMessage.success('登录成功')
    const redirect = route.query.redirect as string || '/dashboard'
    router.push(redirect)
  }
}
</script>

<style scoped>
.login-page {
  min-height: calc(100vh - 60px);
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  display: flex;
  width: 900px;
  min-height: 500px;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-left {
  flex: 1;
  padding: 60px 40px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9));
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.brand h1 {
  font-size: 32px;
  margin: 0 0 8px;
}

.brand p {
  opacity: 0.9;
  margin: 0 0 40px;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
}

.feature-item .el-icon {
  font-size: 24px;
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.login-card {
  width: 100%;
  border: none;
  box-shadow: none;
}

.login-card h2 {
  margin: 0 0 8px;
  color: #1a1a2e;
}

.subtitle {
  color: #666;
  margin: 0 0 32px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.login-btn:hover {
  background: linear-gradient(135deg, #5a6fd6 0%, #6a4190 100%);
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  color: #666;
}

.login-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.token-login-divider {
  text-align: center;
  margin: 20px 0;
  position: relative;
}

.token-login-divider::before,
.token-login-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background: #dcdfe6;
}

.token-login-divider::before {
  left: 0;
}

.token-login-divider::after {
  right: 0;
}

.token-login-divider span {
  background: white;
  padding: 0 12px;
  color: #999;
  font-size: 13px;
}

.token-login-btn {
  width: 100%;
  height: 40px;
  border-radius: 8px;
  font-size: 14px;
  color: #667eea;
  border-color: #667eea;
}

.token-login-btn:hover {
  background: #f0f5ff;
  color: #5a6fd6;
  border-color: #5a6fd6;
}
</style>
