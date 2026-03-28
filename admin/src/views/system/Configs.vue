<!-- 系统配置管理页面 -->
<template>
  <div class="configs-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>系统配置</h1>
      <div class="header-actions">
        <el-button type="info" :icon="DataAnalysis" @click="showCacheStats">缓存统计</el-button>
        <el-button type="primary" :icon="Plus" @click="handleCreate">新增配置</el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input v-model="searchText" placeholder="搜索配置键" clearable style="width: 240px" :prefix-icon="Search"
        @input="handleSearch" />
      <el-select v-model="filterGroup" placeholder="分组" clearable style="width: 160px" @change="loadConfigs">
        <el-option v-for="g in groups" :key="g" :label="g" :value="g" />
      </el-select>
      <el-select v-model="filterActive" placeholder="状态" clearable style="width: 100px" @change="loadConfigs">
        <el-option label="启用" :value="true" />
        <el-option label="禁用" :value="false" />
      </el-select>
      <el-checkbox v-model="includeSecrets" @change="loadConfigs">显示敏感值</el-checkbox>
      <el-button :icon="Refresh" @click="loadConfigs">刷新</el-button>
      <el-button :icon="Delete" type="warning" @click="handleRefreshCache()">清除所有缓存</el-button>
      <el-button :icon="Delete" type="warning" @click="handleRefreshGroupCache" v-if="filterGroup">清除分组缓存</el-button>
    </div>

    <!-- 配置列表 -->
    <div class="table-container">
      <el-table :data="configs" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="key" label="配置键" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="key-cell">
              <span class="key-text">{{ row.key }}</span>
              <el-icon v-if="row.is_secret" class="secret-icon" title="敏感配置">
                <Lock />
              </el-icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="配置值" min-width="250">
          <template #default="{ row }">
            <div class="value-cell">
              <template v-if="typeof row.value === 'object'">
                <el-button link type="primary" @click="viewJsonValue(row)">查看 JSON</el-button>
              </template>
              <template v-else>
                <span class="value-text">{{ formatValue(row.value) }}</span>
              </template>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="value_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.value_type" size="small" type="info">{{ row.value_type }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="group" label="分组" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.group" size="small">{{ row.group }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" size="small" @change="handleToggleActive(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除此配置？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="showDialog" :title="dialogMode === 'create' ? '新增配置' : '编辑配置'" width="1000px" destroy-on-close>
      <el-form ref="formRef" :model="configForm" :rules="formRules" label-width="100px">
        <el-form-item label="配置键" prop="key">
          <el-input v-model="configForm.key" :disabled="dialogMode === 'edit'" placeholder="例如: app.export.format" />
        </el-form-item>

        <el-form-item label="值类型" prop="value_type">
          <el-select v-model="configForm.value_type" style="width: 100%" @change="handleValueTypeChange">
            <el-option label="字符串 (string)" value="string" />
            <el-option label="数字 (number)" value="number" />
            <el-option label="布尔 (boolean)" value="boolean" />
            <el-option label="JSON对象 (json)" value="json" />
            <el-option label="数组 (array)" value="array" />
          </el-select>
        </el-form-item>

        <el-form-item label="配置值" :prop="['json', 'array'].includes(configForm.value_type) ? 'valueJson' : 'value'">
          <template v-if="configForm.value_type === 'boolean'">
            <el-switch v-model="configForm.value" />
          </template>
          <template v-else-if="configForm.value_type === 'number'">
            <el-input-number v-model="configForm.value" :controls="false" style="width: 100%" />
          </template>
          <template v-else-if="configForm.value_type === 'array'">
            <!-- 数组可视化编辑 -->
            <div class="array-editor">
              <el-radio-group v-model="arrayEditMode" size="small" style="margin-bottom: 12px">
                <el-radio-button value="visual">可视化</el-radio-button>
                <el-radio-button value="json">JSON</el-radio-button>
              </el-radio-group>

              <template v-if="arrayEditMode === 'visual'">
                <div v-for="(_item, index) in arrayItems" :key="index" class="array-item">
                  <el-input v-model="arrayItems[index]" placeholder="请输入值" />
                  <el-button :icon="Delete" type="danger" text @click="removeArrayItem(index)" />
                </div>
                <el-button :icon="Plus" type="primary" text @click="addArrayItem">添加项</el-button>
              </template>
              <template v-else>
                <el-input v-model="configForm.valueJson" type="textarea" :rows="6" placeholder="请输入有效的 JSON 数组" />
              </template>
            </div>
          </template>
          <template v-else-if="configForm.value_type === 'json'">
            <!-- JSON对象可视化编辑 -->
            <div class="json-editor">
              <el-radio-group v-model="jsonEditMode" size="small" style="margin-bottom: 12px">
                <el-radio-button value="visual">可视化</el-radio-button>
                <el-radio-button value="json">JSON</el-radio-button>
              </el-radio-group>

              <template v-if="jsonEditMode === 'visual'">
                <div v-for="(_item, index) in jsonPairs" :key="index" class="json-pair">
                  <el-input v-model="jsonPairs[index]!.key" placeholder="键" style="width: 40%" />
                  <el-input v-model="jsonPairs[index]!.value" placeholder="值" style="width: 50%" />
                  <el-button :icon="Delete" type="danger" text @click="removeJsonPair(index)" />
                </div>
                <el-button :icon="Plus" type="primary" text @click="addJsonPair">添加键值对</el-button>
              </template>
              <template v-else>
                <el-input v-model="configForm.valueJson" type="textarea" :rows="6" placeholder="请输入有效的 JSON 对象" />
              </template>
            </div>
          </template>
          <template v-else>
            <el-input v-model="configForm.value" type="textarea" :rows="3" />
          </template>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分组">
              <el-select v-model="configForm.group" filterable allow-create clearable style="width: 100%">
                <el-option v-for="g in groups" :key="g" :label="g" :value="g" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="敏感配置">
              <el-switch v-model="configForm.is_secret" />
              <span class="form-tip" style="margin-left: 8px">敏感配置的值将被掩码显示</span>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input v-model="configForm.remark" type="textarea" :rows="2" placeholder="配置说明" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <!-- JSON 查看对话框 -->
    <el-dialog v-model="showJsonDialog" title="配置值详情" width="600px">
      <div class="json-viewer">
        <pre>{{ jsonViewContent }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { configApi, type AppConfig, type ConfigCreate, type ConfigUpdate } from '@/api/config'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Search, Refresh, Lock, Delete, DataAnalysis } from '@element-plus/icons-vue'

// 列表相关
const loading = ref(false)
const configs = ref<AppConfig[]>([])
const groups = ref<string[]>([])

// 筛选条件
const searchText = ref('')
const filterGroup = ref('')
const filterActive = ref<boolean | ''>('')
const includeSecrets = ref(false)

// 对话框
const showDialog = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentConfig = ref<AppConfig | null>(null)
const submitting = ref(false)
const formRef = ref<FormInstance>()

// JSON 查看
const showJsonDialog = ref(false)
const jsonViewContent = ref('')

const configForm = reactive({
  key: '',
  value: '' as any,
  valueJson: '',
  value_type: 'string',
  group: '',
  remark: '',
  is_secret: false
})

// 数组和JSON编辑模式
const arrayEditMode = ref<'visual' | 'json'>('visual')
const jsonEditMode = ref<'visual' | 'json'>('visual')
const arrayItems = ref<string[]>([])
const jsonPairs = ref<Array<{ key: string; value: string }>>([])

const formRules = computed<FormRules>(() => {
  const isJsonType = ['json', 'array'].includes(configForm.value_type)
  return {
    key: [
      { required: true, message: '请输入配置键', trigger: 'blur' },
      { pattern: /^[a-zA-Z0-9_.:-]+$/, message: '只能包含字母、数字、点、下划线、冒号、横线', trigger: 'blur' }
    ],
    value: isJsonType ? [] : [{ required: true, message: '请输入配置值', trigger: 'blur' }],
    valueJson: isJsonType ? [
      { required: true, message: '请输入配置值', trigger: 'blur' },
      {
        validator: (_rule: any, value: any, callback: any) => {
          try {
            JSON.parse(value)
            callback()
          } catch (e) {
            callback(new Error('JSON 格式无效'))
          }
        },
        trigger: 'blur'
      }
    ] : []
  }
})

// 简单防抖
function debounce<T extends (...args: any[]) => any>(fn: T, delay: number): T {
  let timer: ReturnType<typeof setTimeout> | null = null
  return ((...args: any[]) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }) as T
}

// 工具函数
function formatValue(value: any): string {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'boolean') return value ? '是' : '否'
  if (typeof value === 'string' && value.length > 100) return value.slice(0, 100) + '...'
  return String(value)
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

// 加载配置列表
async function loadConfigs() {
  loading.value = true
  try {
    const params: any = {}
    if (searchText.value) params.search = searchText.value
    if (filterGroup.value) params.group = filterGroup.value
    if (filterActive.value !== '') params.is_active = filterActive.value
    params.include_secrets = includeSecrets.value

    const res = await configApi.list(params)
    configs.value = res.items
  } catch (error) {
    ElMessage.error('加载配置列表失败')
  } finally {
    loading.value = false
  }
}

// 加载分组列表
async function loadGroups() {
  try {
    const res = await configApi.listGroups()
    groups.value = res.groups
  } catch (error) {
    console.error('Failed to load groups:', error)
  }
}

const handleSearch = debounce(() => {
  loadConfigs()
}, 300)

// 新增
function handleCreate() {
  dialogMode.value = 'create'
  currentConfig.value = null
  resetForm()
  showDialog.value = true
}

// 编辑
function handleEdit(config: AppConfig) {
  dialogMode.value = 'edit'
  currentConfig.value = config

  // 根据值类型设置表单
  let valueType = config.value_type || 'string'
  if (!['string', 'number', 'boolean', 'json', 'array'].includes(valueType)) {
    valueType = typeof config.value === 'object' ? 'json' : 'string'
  }

  Object.assign(configForm, {
    key: config.key,
    value: config.value,
    valueJson: typeof config.value === 'object' ? JSON.stringify(config.value, null, 2) : '',
    value_type: valueType,
    group: config.group || '',
    remark: config.remark || '',
    is_secret: config.is_secret
  })

  // 初始化可视化编辑器
  if (valueType === 'array' && Array.isArray(config.value)) {
    arrayItems.value = config.value.map(v => String(v))
    arrayEditMode.value = 'visual'
  } else if (valueType === 'json' && typeof config.value === 'object' && !Array.isArray(config.value)) {
    jsonPairs.value = Object.entries(config.value).map(([k, v]) => ({ key: k, value: String(v) }))
    jsonEditMode.value = 'visual'
  }

  showDialog.value = true
}

function resetForm() {
  Object.assign(configForm, {
    key: '',
    value: '',
    valueJson: '',
    value_type: 'string',
    group: '',
    remark: '',
    is_secret: false
  })
  arrayItems.value = []
  jsonPairs.value = []
  arrayEditMode.value = 'visual'
  jsonEditMode.value = 'visual'
}

function handleValueTypeChange(type: string) {
  // 重置值
  if (type === 'boolean') {
    configForm.value = false
  } else if (type === 'number') {
    configForm.value = 0
  } else if (type === 'json') {
    configForm.value = {}
    configForm.valueJson = '{}'
    jsonPairs.value = []
    jsonEditMode.value = 'visual'
  } else if (type === 'array') {
    configForm.value = []
    configForm.valueJson = '[]'
    arrayItems.value = []
    arrayEditMode.value = 'visual'
  } else {
    configForm.value = ''
  }
}

// 数组编辑器方法
function addArrayItem() {
  arrayItems.value.push('')
}

function removeArrayItem(index: number) {
  arrayItems.value.splice(index, 1)
}

// JSON编辑器方法
function addJsonPair() {
  jsonPairs.value.push({ key: '', value: '' })
}

function removeJsonPair(index: number) {
  jsonPairs.value.splice(index, 1)
}

// 提交表单
async function submitForm() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    // 处理值
    let finalValue = configForm.value

    if (configForm.value_type === 'array') {
      if (arrayEditMode.value === 'visual') {
        // 从可视化编辑器获取数组
        finalValue = arrayItems.value.filter(item => item !== '')
      } else {
        // 从JSON文本解析
        try {
          finalValue = JSON.parse(configForm.valueJson)
          if (!Array.isArray(finalValue)) {
            ElMessage.error('数组格式无效')
            return
          }
        } catch (e) {
          ElMessage.error('JSON 格式无效')
          return
        }
      }
    } else if (configForm.value_type === 'json') {
      if (jsonEditMode.value === 'visual') {
        // 从可视化编辑器构建对象
        finalValue = {}
        for (const pair of jsonPairs.value) {
          if (pair.key) {
            finalValue[pair.key] = pair.value
          }
        }
      } else {
        // 从JSON文本解析
        try {
          finalValue = JSON.parse(configForm.valueJson)
          if (Array.isArray(finalValue) || typeof finalValue !== 'object') {
            ElMessage.error('JSON对象格式无效')
            return
          }
        } catch (e) {
          ElMessage.error('JSON 格式无效')
          return
        }
      }
    }

    submitting.value = true
    try {
      if (dialogMode.value === 'create') {
        const payload: ConfigCreate = {
          key: configForm.key,
          value: finalValue,
          value_type: configForm.value_type,
          group: configForm.group || undefined,
          remark: configForm.remark || undefined,
          is_secret: configForm.is_secret
        }
        await configApi.create(payload)
        ElMessage.success('配置创建成功')
      } else if (currentConfig.value) {
        const payload: ConfigUpdate = {
          value: finalValue,
          value_type: configForm.value_type,
          group: configForm.group || undefined,
          remark: configForm.remark || undefined,
          is_secret: configForm.is_secret
        }
        await configApi.update(currentConfig.value.id, payload)
        ElMessage.success('配置更新成功')
      }
      showDialog.value = false
      loadConfigs()
      loadGroups()
    } catch (error: any) {
      ElMessage.error(error?.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 切换启用状态
async function handleToggleActive(config: AppConfig) {
  try {
    await configApi.update(config.id, { is_active: config.is_active })
    ElMessage.success(config.is_active ? '已启用' : '已禁用')
  } catch (error) {
    config.is_active = !config.is_active
    ElMessage.error('操作失败')
  }
}

// 删除
async function handleDelete(id: number) {
  try {
    await configApi.delete(id)
    ElMessage.success('配置已删除')
    loadConfigs()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '删除失败')
  }
}

// 查看 JSON 值
function viewJsonValue(config: AppConfig) {
  jsonViewContent.value = JSON.stringify(config.value, null, 2)
  showJsonDialog.value = true
}

// 刷新缓存
async function handleRefreshCache(key?: string) {
  try {
    const params: any = {}
    if (key) {
      params.key = key
    }

    const res = await configApi.refreshCache(params)
    ElMessage.success(res.message || '缓存已刷新')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '刷新缓存失败')
  }
}

// 刷新分组缓存
async function handleRefreshGroupCache() {
  if (!filterGroup.value) return

  try {
    const res = await configApi.refreshCache({ group: filterGroup.value })
    ElMessage.success(res.message || `已刷新分组缓存: ${filterGroup.value}`)
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '刷新缓存失败')
  }
}

// 显示缓存统计
async function showCacheStats() {
  try {
    const stats = await configApi.getCacheStats()
    ElMessage.info({
      message: `缓存统计: 总计 ${stats.total_cached} 项, 前缀: ${stats.cache_prefix}, 默认TTL: ${stats.default_ttl}秒`,
      duration: 5000
    })
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '获取缓存统计失败')
  }
}

onMounted(() => {
  loadConfigs()
  loadGroups()
})
</script>

<style scoped>
.configs-page {
  padding: 24px;
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
  box-sizing: border-box;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
}

.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.table-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.key-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.key-text {
  font-family: 'Consolas', 'Monaco', monospace;
  color: #409eff;
}

.secret-icon {
  color: #e6a23c;
}

.value-cell {
  max-width: 300px;
  overflow: hidden;
}

.value-text {
  word-break: break-all;
}

.text-muted {
  color: #909399;
}

.form-tip {
  font-size: 12px;
  color: #909399;
}

.json-viewer {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  max-height: 400px;
  overflow: auto;
}

.json-viewer pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 数组编辑器 */
.array-editor,
.json-editor {
  width: 100%;
}

.array-item {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.array-item .el-input {
  flex: 1;
}

.json-pair {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.json-pair .el-input:first-child {
  font-family: 'Consolas', 'Monaco', monospace;
}
</style>
