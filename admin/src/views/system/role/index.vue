<template>
  <div class="page-container">
    <div class="page-header">
      <h2>角色管理</h2>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleCreate">新增角色</el-button>
        <el-button :icon="Refresh" @click="loadData">刷新</el-button>
      </div>
    </div>

    <div class="table-container">
      <el-table v-loading="loading" :data="tableData" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" min-width="120" />
        <el-table-column prop="code" label="角色编码" min-width="120" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column prop="remark" label="备注" min-width="180" />
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
            <el-button type="success" link @click="handlePerms(row)">权限</el-button>
            <el-popconfirm title="确定删除该角色吗？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '新增角色' : '编辑角色'"
      width="500px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入角色编码" :disabled="dialogType === 'edit'" />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="form.sort" :min="0" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入备注" />
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

    <!-- 权限设置对话框 -->
    <el-dialog
      v-model="permDialogVisible"
      title="权限设置"
      width="500px"
      destroy-on-close
    >
        <div style="max-height: 400px; overflow-y: auto;">
            <el-tree
                ref="treeRef"
                :data="menuTree"
                :props="{ label: 'menu_name', children: 'children' }"
                node-key="id"
                show-checkbox
                default-expand-all
            />
        </div>
        <template #footer>
            <el-button @click="permDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitPerms" :loading="submittingPerms">保存</el-button>
        </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { roleApi, menuApi, type Role } from '@/api/system'
import dayjs from 'dayjs'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref<Role[]>([])

const dialogVisible = ref(false)
const dialogType = ref<'create' | 'edit'>('create')
const formRef = ref()

const form = reactive({
  id: 0,
  name: '',
  code: '',
  sort: 0,
  remark: '',
  enable_status: 1
})

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }]
}

// Permissions
const permDialogVisible = ref(false)
const submittingPerms = ref(false)
const currentRoleId = ref(0)
const menuTree = ref([])
const treeRef = ref()

onMounted(() => {
  loadData()
  loadMenuTree()
})

async function loadData() {
  loading.value = true
  try {
    const res = await roleApi.list()
    // Handle PageResult or array depending on implementation
    if (res.items) {
        tableData.value = res.items
    } else { // Fallback if API returns array directly
        tableData.value = res as any
    }
  } catch(e) {
      console.error(e)
  } finally {
    loading.value = false
  }
}
async function loadMenuTree() {
    try {
        const res = await menuApi.getTree()
        menuTree.value = res as any
        // If empty, mock for demo
        if (!res || (Array.isArray(res) && res.length === 0)) {
            // Mock data
            // menuTree.value = [{ id: 1, menu_name: 'System', children: [{ id: 2, menu_name: 'User' }] }]
        }
    } catch {
        // Mock if failed
    }
}

function handleCreate() {
  dialogType.value = 'create'
  form.id = 0
  form.name = ''
  form.code = ''
  form.sort = 0
  form.remark = ''
  form.enable_status = 1
  dialogVisible.value = true
}

function handleEdit(row: Role) {
  dialogType.value = 'edit'
  form.id = row.id
  form.name = row.name
  form.code = row.code
  form.sort = row.sort
  form.remark = row.remark || ''
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
        await roleApi.create(form)
        ElMessage.success('创建成功')
      } else {
        await roleApi.update(form.id, form)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      loadData()
    } catch {
        // fail
    } finally {
      submitting.value = false
    }
  })
}

async function handleStatusChange(row: Role) {
    try {
        await roleApi.update(row.id, { enable_status: row.enable_status })
        ElMessage.success('状态已更新')
    } catch {
        row.enable_status = row.enable_status === 1 ? 0 : 1
    }
}

async function handleDelete(row: Role) {
  try {
    await roleApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {
      //
  }
}

async function handlePerms(row: Role) {
    currentRoleId.value = row.id
    permDialogVisible.value = true
    // 加载当前角色已分配的菜单ID并勾选
    try {
        const menuIds = await roleApi.getMenus(row.id)
        // nextTick to ensure tree is rendered
        setTimeout(() => {
            if (treeRef.value) {
                // 只设置叶子节点的 key，el-tree 会自动推导父节点的半选/全选状态
                // 如果直接 setCheckedKeys 包含父节点 ID，会导致其所有子节点被全选
                const leafKeys = (menuIds || []).filter((id: number) => {
                    const node = treeRef.value.getNode(id)
                    return node && node.isLeaf
                })
                treeRef.value.setCheckedKeys(leafKeys)
            }
        }, 100)
    } catch {
        //
    }
}

async function submitPerms() {
    submittingPerms.value = true
    try {
        // 获取全选和半选的菜单ID (半选=父级目录部分子级被选中)
        const checkedKeys = treeRef.value.getCheckedKeys() || []
        const halfCheckedKeys = treeRef.value.getHalfCheckedKeys() || []
        const allKeys = [...checkedKeys, ...halfCheckedKeys]
        await roleApi.setMenus(currentRoleId.value, allKeys)
        ElMessage.success('权限设置成功')
        permDialogVisible.value = false
    } catch {
        //
    } finally {
        submittingPerms.value = false
    }
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
.table-container {
  background: white;
  padding: 24px;
  border-radius: 8px;
}
</style>
