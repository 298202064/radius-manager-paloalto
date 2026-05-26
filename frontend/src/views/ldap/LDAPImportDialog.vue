<template>
  <el-dialog
    :model-value="visible"
    title="导入 AD 用户"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- Step 1: Search -->
    <template v-if="!searched">
      <el-form ref="searchFormRef" :model="searchForm" label-width="100px">
        <el-form-item label="搜索过滤器">
          <el-input v-model="searchForm.search_filter" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="搜索 Base">
          <el-input v-model="searchForm.search_base" placeholder="留空则使用配置中的 Base DN" />
        </el-form-item>
      </el-form>
      <div style="text-align: center; margin-top: 12px">
        <el-button type="primary" :loading="searching" @click="handleSearch">搜索用户</el-button>
      </div>
    </template>

    <!-- Step 2: Results -->
    <template v-else>
      <div style="margin-bottom: 12px; color: #909399; font-size: 13px">
        共找到 <strong>{{ users.length }}</strong> 个用户
      </div>
      <div style="margin-bottom: 12px">
        <el-button size="small" @click="selectAll">全选</el-button>
        <el-button size="small" @click="selectedUsers = []">取消全选</el-button>
        <el-button size="small" type="primary" :loading="importing"
          :disabled="selectedUsers.length === 0"
          @click="handleImport">
          导入选中用户 ({{ selectedUsers.length }})
        </el-button>
      </div>
      <el-table :data="users" v-loading="searching" stripe height="360"
        @selection-change="(rows: any[]) => selectedUsers = rows.map(r => r.username)">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="username" label="用户名" width="160" />
        <el-table-column prop="display_name" label="显示名称" width="160" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="dn" label="DN" min-width="200" show-overflow-tooltip />
      </el-table>

      <div v-if="importResult" style="margin-top: 12px">
        <el-alert
          :title="`导入完成: 成功 ${importResult.total_imported} 人，跳过 ${importResult.total_skipped} 人（已存在）`"
          :type="importResult.total_imported > 0 ? 'success' : 'info'"
          show-icon
        />
      </div>
    </template>

    <template #footer>
      <el-button v-if="searched" @click="resetSearch">重新搜索</el-button>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { searchADUsers, importADUsers } from '@/api/ldap'

const props = defineProps<{ visible: boolean; configId: number }>()
const emit = defineEmits(['update:visible', 'imported'])

const searching = ref(false)
const importing = ref(false)
const searched = ref(false)
const users = ref<any[]>([])
const selectedUsers = ref<string[]>([])
const importResult = ref<any>(null)

const searchFormRef = ref<FormInstance>()
const searchForm = reactive({
  search_filter: '(&(objectClass=user)(objectCategory=person))',
  search_base: '',
})

function handleClose() {
  emit('update:visible', false)
}

function resetSearch() {
  searched.value = false
  users.value = []
  selectedUsers.value = []
  importResult.value = null
}

function selectAll() {
  selectedUsers.value = users.value.map(u => u.username)
}

async function handleSearch() {
  searching.value = true
  try {
    const res = await searchADUsers(props.configId, {
      search_filter: searchForm.search_filter,
      search_base: searchForm.search_base || undefined,
    })
    users.value = res.data.items
    searched.value = true
  } catch {
    users.value = []
  } finally {
    searching.value = false
  }
}

async function handleImport() {
  if (selectedUsers.value.length === 0) return
  importing.value = true
  try {
    const res = await importADUsers(props.configId, { usernames: selectedUsers.value })
    importResult.value = res.data
    ElMessage.success(`成功导入 ${res.data.total_imported} 人`)
    emit('imported')
  } finally {
    importing.value = false
  }
}
</script>
