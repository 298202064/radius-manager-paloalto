<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>用户管理</h2>
      <el-button type="primary" @click="openCreateDialog">新建用户</el-button>
    </div>

    <!-- Search -->
    <el-card shadow="never" style="margin-bottom: 16px">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="搜索">
          <el-input v-model="searchForm.search" placeholder="用户名/邮箱" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.enabled" placeholder="全部" clearable style="width: 120px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card shadow="never">
      <el-table :data="users" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="role" label="角色" width="80">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
              {{ row.role === 'admin' ? '管理' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'danger'" size="small">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="OTP" width="80">
          <template #default="{ row }">
            <el-tag :type="row.has_otp ? 'warning' : 'info'" size="small">
              {{ row.has_otp ? '已绑定' : '未绑定' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="note" label="备注" min-width="150" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button
              size="small"
              :type="row.has_otp ? 'warning' : 'info'"
              @click="showOtpStatus(row)"
            >
              OTP
            </el-button>
            <el-popconfirm title="确定删除该用户？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div style="display: flex; justify-content: flex-end; margin-top: 16px">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="fetchUsers"
        />
      </div>
    </el-card>

    <!-- Create/Edit Dialog -->
    <UserFormDialog
      v-model:visible="dialogVisible"
      :user="editingUser"
      @saved="fetchUsers"
    />

    <!-- OTP Status Dialog -->
    <el-dialog v-model="otpDialogVisible" title="OTP状态" width="400px">
      <div v-if="otpStatus">
        <p>状态: <el-tag :type="otpStatus.enabled ? 'warning' : 'info'" size="small">
          {{ otpStatus.enabled ? '已绑定' : '未绑定' }}
        </el-tag></p>
        <p>设备: {{ otpStatus.device_name }}</p>
        <p>是否有设备: {{ otpStatus.has_device ? '是' : '否' }}</p>
        <el-button
          v-if="otpStatus.has_device"
          type="danger"
          size="small"
          style="margin-top: 12px"
          @click="handleDisableOtp"
        >
          解除绑定
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getUsers, deleteUser, getUserOtpStatus, adminDisableUserOtp } from '@/api/users'
import UserFormDialog from './UserFormDialog.vue'

const loading = ref(false)
const users = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editingUser = ref<any>(null)
const otpDialogVisible = ref(false)
const otpStatus = ref<any>(null)
const otpUserId = ref<number>(0)

const searchForm = reactive({
  search: '',
  enabled: null as boolean | null,
})

function fetchUsers() {
  loading.value = true
  getUsers({
    page: page.value,
    page_size: pageSize.value,
    search: searchForm.search,
    enabled: searchForm.enabled,
  })
    .then((res) => {
      users.value = res.data.items
      total.value = res.data.total
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearch() {
  page.value = 1
  fetchUsers()
}

function resetSearch() {
  searchForm.search = ''
  searchForm.enabled = null
  handleSearch()
}

function openCreateDialog() {
  editingUser.value = null
  dialogVisible.value = true
}

function openEditDialog(user: any) {
  editingUser.value = user
  dialogVisible.value = true
}

async function handleDelete(id: number) {
  try {
    await deleteUser(id)
    ElMessage.success('用户已删除')
    fetchUsers()
  } catch {
    // handled by interceptor
  }
}

async function showOtpStatus(user: any) {
  otpUserId.value = user.id
  try {
    const res = await getUserOtpStatus(user.id)
    otpStatus.value = res.data
    otpDialogVisible.value = true
  } catch {
    // handled by interceptor
  }
}

async function handleDisableOtp() {
  try {
    await adminDisableUserOtp(otpUserId.value)
    ElMessage.success('OTP已解除绑定')
    otpDialogVisible.value = false
    fetchUsers()
  } catch {
    // handled by interceptor
  }
}

onMounted(fetchUsers)
</script>
