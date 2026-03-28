<template>
  <div class="page-container">
    <div class="page-header">
      <h2>用户管理</h2>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleCreate">新增用户</el-button>
        <el-button :icon="Refresh" @click="loadData">刷新</el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-form :inline="true" :model="queryParams" class="demo-form-inline">
        <el-form-item label="用户名">
          <el-input v-model="queryParams.username" placeholder="请输入用户名" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.enable_status" placeholder="全部" clearable style="width: 120px">
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <div class="table-container">
      <el-table v-loading="loading" :data="tableData" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="nickname" label="昵称" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="feishu_id" label="飞书ID" min-width="120" />
        <el-table-column prop="roles" label="角色" min-width="150">
             <template #default="{ row }">
                 <el-tag v-for="role in row.roles" :key="role.id" size="small" style="margin-right: 5px">{{ role.name }}</el-tag>
             </template>
        </el-table-column>
        <el-table-column prop="enable_status" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.enable_status"
              :active-value="1"
              :inactive-value="0"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180">
            <template #default="{ row }">
                {{ formatTime(row.create_time) }}
            </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleResetPassword(row)">重置密码</el-button>
            <el-popconfirm title="确定删除该用户吗？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '新增用户' : '编辑用户'"
      width="500px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="dialogType === 'edit'" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="dialogType === 'create'">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
         <el-form-item label="飞书ID" prop="feishu_id">
          <el-input v-model="form.feishu_id" placeholder="请输入飞书ID" />
        </el-form-item>
        <el-form-item label="角色" prop="role_ids">
          <el-select v-model="form.role_ids" multiple placeholder="请选择角色" style="width: 100%">
             <el-option
                v-for="item in roleOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
             />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="enable_status">
            <el-radio-group v-model="form.enable_status">
                <el-radio :label="1">启用</el-radio>
                <el-radio :label="0">禁用</el-radio>
            </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { userApi, roleApi, type User, type Role } from '@/api/system'
import dayjs from 'dayjs'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref<User[]>([])
const total = ref(0)
const roleOptions = ref<Role[]>([])

const queryParams = reactive({
  page: 1,
  page_size: 20,
  username: '',
  enable_status: undefined as number | undefined
})

const dialogVisible = ref(false)
const dialogType = ref<'create' | 'edit'>('create')
const formRef = ref()

const form = reactive({
  id: 0,
  username: '',
  nickname: '',
  password: '',
  email: '',
  feishu_id: '',
  role_ids: [] as number[],
  enable_status: 1
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
  role_ids: [{ required: true, type: 'array', min: 1, message: '请选择至少一个角色', trigger: 'change' }]
}

onMounted(() => {
  loadData()
  loadRoles()
})

async function loadData() {
  loading.value = true
  try {
    const res = await userApi.list(queryParams)
    tableData.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function loadRoles() {
    try {
        const res = await roleApi.getAll()
        roleOptions.value = res
    } catch (e) {
        console.error('Failed to load roles', e)
    }
}

function resetQuery() {
  queryParams.username = ''
  queryParams.enable_status = undefined
  queryParams.page = 1
  loadData()
}

function handleCreate() {
  dialogType.value = 'create'
  form.id = 0
  form.username = ''
  form.nickname = ''
  form.password = ''
  form.email = ''
  form.feishu_id = ''
  form.role_ids = []
  form.enable_status = 1
  dialogVisible.value = true
}

function handleEdit(row: User) {
  dialogType.value = 'edit'
  form.id = row.id
  form.username = row.username
  form.nickname = row.nickname
  form.password = '' // Don't show password
  form.email = row.email || ''
  form.feishu_id = row.feishu_id || ''
  form.role_ids = row.roles?.map(r => r.id) || []
  form.enable_status = row.enable_status
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    submitting.value = true
    try {
      if (dialogType.value === 'create') {
        await userApi.create(form)
        ElMessage.success('创建成功')
      } else {
        const { password, ...updateData } = form
        // Remove password from update if empty
        await userApi.update(form.id, updateData)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      loadData()
    } finally {
      submitting.value = false
    }
  })
}

async function handleStatusChange(row: User) {
    try {
        await userApi.update(row.id, { enable_status: row.enable_status })
        ElMessage.success('状态已更新')
    } catch {
        row.enable_status = row.enable_status === 1 ? 0 : 1 // revert
    }
}

async function handleDelete(row: User) {
  try {
    await userApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // handled by request interceptor
  }
}

function handleResetPassword(row: User) {
  ElMessageBox.prompt('请输入新密码', '重置密码', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /^.{6,}$/,
    inputErrorMessage: '密码至少6位'
  }).then(async (data: any) => {
    await userApi.resetPassword(row.id, data.value)
    ElMessage.success('密码重置成功')
  })
}

function formatTime(time: string) {
    if (!time) return '-'
    return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}
</script>

<style scoped>
.page-container {
  padding: 24px;
  background: #f0f2f5;
  min-height: calc(100vh - 60px); box-sizing: border-box;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.filter-bar {
  background: white;
  padding: 16px 24px 0;
  border-radius: 8px;
  margin-bottom: 16px;
}
.table-container {
  background: white;
  padding: 24px;
  border-radius: 8px;
}
.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
