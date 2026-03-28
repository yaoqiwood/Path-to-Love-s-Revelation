<template>
  <div class="page-container">
    <div class="page-header">
      <h2>参与者管理</h2>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleCreate">新增参与者</el-button>
        <el-button :icon="Refresh" @click="loadData">刷新</el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-form :inline="true" :model="queryParams" class="demo-form-inline">
        <el-form-item label="姓名">
          <el-input v-model="queryParams.participant_name" placeholder="请输入姓名" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="queryParams.gender" placeholder="全部" clearable style="width: 120px">
            <el-option label="男" :value="1" />
            <el-option label="女" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="MBTI">
          <el-select v-model="queryParams.mbti" placeholder="全部" clearable style="width: 140px" filterable>
            <el-option v-for="item in mbtiOptions" :key="item" :label="item" :value="item" />
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
        <el-table-column prop="participant_name" label="姓名" min-width="120" />
        <el-table-column prop="permanent_token" label="永久Token" min-width="180" show-overflow-tooltip />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="{ row }">
            <el-tag :type="genderTagType(row.gender)" size="small">{{ genderLabel(row.gender) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="mbti" label="MBTI" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.mbti" type="info" size="small" effect="plain">{{ row.mbti }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="hometown" label="籍贯" min-width="120" show-overflow-tooltip />
        <el-table-column prop="current_residence" label="现住地" min-width="120" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除该参与者吗？" @confirm="handleDelete(row)">
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
      :title="dialogType === 'create' ? '新增参与者' : '编辑参与者'"
      width="500px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="姓名" prop="participant_name">
          <el-input v-model="form.participant_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="永久Token" v-if="dialogType === 'edit'">
          <el-input v-model="form.permanent_token" disabled />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio :value="0">未知</el-radio>
            <el-radio :value="1">男</el-radio>
            <el-radio :value="2">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="form.age" :min="0" :max="150" />
        </el-form-item>
        <el-form-item label="MBTI" prop="mbti">
          <el-select v-model="form.mbti" placeholder="请选择MBTI" clearable filterable style="width: 100%">
            <el-option v-for="item in mbtiOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="籍贯" prop="hometown">
          <el-input v-model="form.hometown" placeholder="请输入籍贯" />
        </el-form-item>
        <el-form-item label="现住地" prop="current_residence">
          <el-input v-model="form.current_residence" placeholder="请输入现住地" />
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
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { participantApi, type Participant } from '@/api/activity'
import dayjs from 'dayjs'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref<Participant[]>([])
const total = ref(0)

const queryParams = reactive({
  page: 1,
  page_size: 20,
  participant_name: '',
  gender: undefined as number | undefined,
  mbti: ''
})

const dialogVisible = ref(false)
const dialogType = ref<'create' | 'edit'>('create')
const formRef = ref()

const form = reactive({
  id: 0,
  participant_name: '',
  permanent_token: '',
  gender: 0,
  age: null as number | null,
  mbti: null as string | null,
  hometown: null as string | null,
  current_residence: null as string | null
})

const rules = {
  participant_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }]
}

// 16种MBTI类型
const mbtiOptions = [
  'INTJ', 'INTP', 'ENTJ', 'ENTP',
  'INFJ', 'INFP', 'ENFJ', 'ENFP',
  'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ',
  'ISTP', 'ISFP', 'ESTP', 'ESFP'
]

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const res = await participantApi.list(queryParams)
    tableData.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function resetQuery() {
  queryParams.participant_name = ''
  queryParams.gender = undefined
  queryParams.mbti = ''
  queryParams.page = 1
  loadData()
}

function handleCreate() {
  dialogType.value = 'create'
  form.id = 0
  form.participant_name = ''
  form.permanent_token = ''
  form.gender = 0
  form.age = null
  form.mbti = null
  form.hometown = null
  form.current_residence = null
  dialogVisible.value = true
}

function handleEdit(row: Participant) {
  dialogType.value = 'edit'
  form.id = row.id
  form.participant_name = row.participant_name
  form.permanent_token = row.permanent_token
  form.gender = row.gender
  form.age = row.age ?? null
  form.mbti = row.mbti ?? null
  form.hometown = row.hometown ?? null
  form.current_residence = row.current_residence ?? null
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    submitting.value = true
    try {
      if (dialogType.value === 'create') {
        await participantApi.create(form)
        ElMessage.success('创建成功')
      } else {
        await participantApi.update(form.id, form)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      loadData()
    } finally {
      submitting.value = false
    }
  })
}

async function handleDelete(row: Participant) {
  try {
    await participantApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // handled by request interceptor
  }
}

function genderLabel(gender: number): string {
  const map: Record<number, string> = { 0: '未知', 1: '男', 2: '女' }
  return map[gender] || '未知'
}

function genderTagType(gender: number): '' | 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<number, '' | 'success' | 'warning' | 'danger' | 'info'> = { 0: 'info', 1: '', 2: 'danger' }
  return map[gender] || 'info'
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
.text-muted {
  color: #c0c4cc;
}
</style>
