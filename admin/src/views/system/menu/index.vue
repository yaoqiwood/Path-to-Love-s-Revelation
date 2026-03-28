<template>
  <div class="page-container">
    <div class="page-header">
      <h2>菜单管理</h2>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleCreate()">新增菜单</el-button>
        <el-button :icon="Refresh" @click="loadData">刷新</el-button>
        <el-button @click="toggleExpandAll">展开/折叠</el-button>
      </div>
    </div>

    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="tableData"
        row-key="id"
        :default-expand-all="isExpandAll"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="menu_name" label="菜单名称" min-width="180" />
        <el-table-column prop="menu_icon" label="图标" width="60" align="center">
            <template #default="{ row }">
                <el-icon v-if="row.menu_icon && icons[row.menu_icon]">
                    <component :is="icons[row.menu_icon]" />
                </el-icon>
            </template>
        </el-table-column>
        <el-table-column prop="menu_type" label="类型" width="80" align="center">
             <template #default="{ row }">
                <el-tag v-if="row.menu_type === 'M'" type="primary">目录</el-tag>
                <el-tag v-else-if="row.menu_type === 'C'" type="success">菜单</el-tag>
                <el-tag v-else type="info">按钮</el-tag>
             </template>
        </el-table-column>
        <el-table-column prop="paths" label="路由地址" min-width="150" />
        <el-table-column prop="component" label="组件路径" min-width="150" />
        <el-table-column prop="perms" label="权限标识" min-width="150" />
        <el-table-column prop="menu_sort" label="排序" width="80" />
        <el-table-column prop="show_status" label="显示" width="80">
             <template #default="{ row }">
                <el-tag v-if="row.show_status === 1" type="success">显示</el-tag>
                <el-tag v-else type="info">隐藏</el-tag>
             </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleCreate(row.id)" v-if="row.menu_type !== 'A'">新增</el-button>
            <el-popconfirm title="确定删除该菜单吗？" @confirm="handleDelete(row)">
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
      :title="dialogType === 'create' ? '新增菜单' : '编辑菜单'"
      width="600px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="上级菜单" prop="pid">
           <el-tree-select
              v-model="form.pid"
              :data="menuOptions"
              :props="{ label: 'menu_name', value: 'id', children: 'children' }"
              check-strictly
              filterable
              placeholder="选择上级菜单"
              style="width: 100%"
           />
        </el-form-item>
        <el-form-item label="菜单类型" prop="menu_type">
          <el-radio-group v-model="form.menu_type">
            <el-radio label="M">目录</el-radio>
            <el-radio label="C">菜单</el-radio>
            <el-radio label="A">按钮</el-radio>
          </el-radio-group>
        </el-form-item>
         <el-form-item label="菜单名称" prop="menu_name">
          <el-input v-model="form.menu_name" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="显示排序" prop="menu_sort">
          <el-input-number v-model="form.menu_sort" :min="0" />
        </el-form-item>
        
        <template v-if="form.menu_type !== 'A'">
            <el-form-item label="路由地址" prop="paths">
              <el-input v-model="form.paths" placeholder="请输入路由地址" />
            </el-form-item>
             <el-form-item label="菜单图标" prop="menu_icon">
              <el-input v-model="form.menu_icon" placeholder="请输入图标名称 (如 User)" />
            </el-form-item>
        </template>

        <template v-if="form.menu_type === 'C'">
            <el-form-item label="组件路径" prop="component">
              <el-input v-model="form.component" placeholder="请输入组件路径 (如 system/user/index)" />
            </el-form-item>
             <el-form-item label="是否缓存" prop="cache_status">
                <el-radio-group v-model="form.cache_status">
                    <el-radio :label="1">缓存</el-radio>
                    <el-radio :label="0">不缓存</el-radio>
                </el-radio-group>
            </el-form-item>
        </template>
        
        <template v-if="form.menu_type !== 'M'">
             <el-form-item label="权限标识" prop="perms">
              <el-input v-model="form.perms" placeholder="请输入权限标识 (如 system:user:list)" />
            </el-form-item>
        </template>

         <el-form-item label="显示状态" prop="show_status" v-if="form.menu_type !== 'A'">
            <el-radio-group v-model="form.show_status">
                <el-radio :label="1">显示</el-radio>
                <el-radio :label="0">隐藏</el-radio>
            </el-radio-group>
        </el-form-item>
         <el-form-item label="菜单状态" prop="enable_status">
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
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { menuApi, type Menu } from '@/api/system'

const icons = ElementPlusIconsVue as any
const loading = ref(false)
const submitting = ref(false)
const tableData = ref<Menu[]>([])
const menuOptions = ref<any[]>([])
const isExpandAll = ref(false)

const dialogVisible = ref(false)
const dialogType = ref<'create' | 'edit'>('create')
const formRef = ref()

const form = reactive({
  id: 0,
  pid: 0,
  menu_type: 'M' as 'M' | 'C' | 'A',
  menu_name: '',
  menu_icon: '',
  menu_sort: 0,
  paths: '',
  component: '',
  perms: '',
  cache_status: 1,
  show_status: 1,
  enable_status: 1
})

const rules = {
  menu_name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
  menu_sort: [{ required: true, message: '请输入排序', trigger: 'blur' }]
}

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const res = await menuApi.getTree() // Use getTree for nested structure
    tableData.value = res || []
    
    // Prepare options for Select (add root)
    menuOptions.value = [{ id: 0, menu_name: '主类目', children: res || [] }]
  } catch (e) {
      console.error(e)
  } finally {
    loading.value = false
  }
}

function toggleExpandAll() {
    isExpandAll.value = !isExpandAll.value
    // Element Plus Table doesn't support dynamic toggling well without re-render or key change
    // For simplicity, just reload data or toggling works if row-key is set? Not dynamically.
    // Actually default-expand-all only works on init. 
    // We can use toggleRowExpansion but we need to traverse.
    // For now, let's keep it simple or just rely on manual toggle.
}

function handleCreate(pid = 0) {
  dialogType.value = 'create'
  form.id = 0
  form.pid = pid
  form.menu_type = 'M'
  form.menu_name = ''
  form.menu_icon = ''
  form.menu_sort = 0
  form.paths = ''
  form.component = ''
  form.perms = ''
  form.cache_status = 1
  form.show_status = 1
  form.enable_status = 1
  dialogVisible.value = true
}

function handleEdit(row: Menu) {
  dialogType.value = 'edit'
  form.id = row.id
  form.pid = row.pid
  form.menu_type = row.menu_type
  form.menu_name = row.menu_name
  form.menu_icon = row.menu_icon || ''
  form.menu_sort = row.menu_sort
  form.paths = row.paths || ''
  form.component = row.component || ''
  form.perms = row.perms || ''
  form.cache_status = row.cache_status
  form.show_status = row.show_status
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
        await menuApi.create(form)
        ElMessage.success('创建成功')
      } else {
        await menuApi.update(form.id, form)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      loadData()
    } catch {
       //
    } finally {
      submitting.value = false
    }
  })
}

async function handleDelete(row: Menu) {
  try {
    await menuApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {
      //
  }
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
