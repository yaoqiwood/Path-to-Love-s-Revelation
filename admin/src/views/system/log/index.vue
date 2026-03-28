<template>
  <div class="page-container">
    <div class="page-header">
      <h2>操作日志</h2>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="loadData">刷新</el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="操作标题">
          <el-input v-model="queryParams.title" placeholder="请输入操作标题" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="操作人">
          <el-input v-model="queryParams.username" placeholder="请输入操作人" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="业务类型">
          <el-select v-model="queryParams.business_type" placeholder="全部" clearable style="width: 120px">
            <el-option label="其它" :value="0" />
            <el-option label="新增" :value="1" />
            <el-option label="修改" :value="2" />
            <el-option label="删除" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="正常" :value="0" />
            <el-option label="异常" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <div class="table-container">
      <el-table v-loading="loading" :data="tableData" stripe style="width: 100%">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-detail">
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="请求URL">{{ row.url }}</el-descriptions-item>
                <el-descriptions-item label="方法名称">{{ row.method }}</el-descriptions-item>
                <el-descriptions-item label="请求参数">
                  <div class="detail-text">{{ row.param || '-' }}</div>
                </el-descriptions-item>
                <el-descriptions-item label="返回参数">
                  <div class="detail-text">{{ row.result || '-' }}</div>
                </el-descriptions-item>
                <el-descriptions-item v-if="row.error" label="错误信息">
                  <div class="detail-text error-text">{{ row.error }}</div>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="操作标题" min-width="120" />
        <el-table-column prop="username" label="操作人" width="120" />
        <el-table-column prop="business_type" label="业务类型" width="100">
          <template #default="{ row }">
            <el-tag :type="businessTypeTag(row.business_type).type" size="small">
              {{ businessTypeTag(row.business_type).label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="request_method" label="请求方式" width="100">
          <template #default="{ row }">
            <el-tag :type="methodTagType(row.request_method)" size="small" effect="plain">
              {{ row.request_method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP" width="140" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 0 ? 'success' : 'danger'" size="small">
              {{ row.status === 0 ? '正常' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cost_time" label="耗时" width="100">
          <template #default="{ row }">
            <span>{{ row.cost_time }}ms</span>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.create_time) }}
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { systemLogApi, type SystemLog } from '@/api/system'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref<SystemLog[]>([])
const total = ref(0)
const dateRange = ref<string[]>([])

const queryParams = reactive({
  page: 1,
  page_size: 20,
  title: '',
  username: '',
  business_type: undefined as number | undefined,
  status: undefined as number | undefined,
  start_time: undefined as string | undefined,
  end_time: undefined as string | undefined,
})

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    // 处理日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      queryParams.start_time = dateRange.value[0] + ' 00:00:00'
      queryParams.end_time = dateRange.value[1] + ' 23:59:59'
    } else {
      queryParams.start_time = undefined
      queryParams.end_time = undefined
    }
    const res = await systemLogApi.list(queryParams)
    tableData.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  queryParams.page = 1
  loadData()
}

function resetQuery() {
  queryParams.title = ''
  queryParams.username = ''
  queryParams.business_type = undefined
  queryParams.status = undefined
  dateRange.value = []
  queryParams.start_time = undefined
  queryParams.end_time = undefined
  queryParams.page = 1
  loadData()
}

function businessTypeTag(type: number) {
  const map: Record<number, { label: string; type: string }> = {
    0: { label: '其它', type: 'info' },
    1: { label: '新增', type: 'success' },
    2: { label: '修改', type: 'warning' },
    3: { label: '删除', type: 'danger' },
  }
  return map[type] || { label: '未知', type: 'info' }
}

function methodTagType(method: string) {
  const map: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info',
  }
  return map[method?.toUpperCase()] || 'info'
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
.expand-detail {
  padding: 12px 24px;
}
.detail-text {
  word-break: break-all;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
}
.error-text {
  color: #f56c6c;
}
</style>
