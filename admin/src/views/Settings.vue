<!-- 设置页面 -->
<template>
  <div class="settings-page">
    <h1>系统设置</h1>
    
    <el-tabs v-model="activeTab" tab-position="left">
      <el-tab-pane label="个人资料" name="profile">
        <el-card>
          <template #header>个人资料</template>
          <el-form :model="profileForm" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            <el-form-item label="姓名">
              <el-input v-model="profileForm.full_name" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveProfile">保存</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>修改密码</template>
          <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
            <el-form-item label="当前密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入当前密码" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码（至少6位）" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="changingPassword" @click="handleChangePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="AI 配置" name="ai">
        <el-card>
          <template #header>AI 服务配置</template>
          <el-form label-width="140px">
            <el-form-item label="Replicate API">
              <el-input type="password" placeholder="请输入 Replicate API Token" show-password />
            </el-form-item>
            <el-form-item label="Stability API">
              <el-input type="password" placeholder="请输入 Stability API Key" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="存储管理" name="storage">
        <el-card>
          <template #header>存储空间</template>
          <div class="storage-info">
            <el-progress type="circle" :percentage="35" :width="120" />
            <div class="storage-details">
              <p>已使用: 3.5 GB / 10 GB</p>
              <el-button type="danger" size="small">清理临时文件</el-button>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { userApi } from '@/api/system'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const activeTab = ref('profile')

const profileForm = reactive({
  username: '',
  email: '',
  full_name: ''
})

async function saveProfile() {
  const success = await userStore.updateProfile({
    email: profileForm.email,
    full_name: profileForm.full_name
  })
  if (success) {
    ElMessage.success('保存成功')
  }
}

onMounted(() => {
  if (userStore.user) {
    profileForm.username = userStore.user.username
    profileForm.email = userStore.user.email || ''
    profileForm.full_name = userStore.user.nickname || ''
  }
})

// ==================== 修改密码 ====================
const passwordFormRef = ref()
const changingPassword = ref(false)

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const passwordRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string, callback: Function) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

async function handleChangePassword() {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    changingPassword.value = true
    try {
      await userApi.changePassword({
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password
      })
      ElMessage.success('密码修改成功')
      passwordForm.old_password = ''
      passwordForm.new_password = ''
      passwordForm.confirm_password = ''
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || '密码修改失败')
    } finally {
      changingPassword.value = false
    }
  })
}
</script>

<style scoped>
.settings-page { padding: 24px; }
.settings-page h1 { margin: 0 0 24px; }
.storage-info { display: flex; align-items: center; gap: 32px; }
.storage-details p { margin: 0 0 12px; }
</style>
