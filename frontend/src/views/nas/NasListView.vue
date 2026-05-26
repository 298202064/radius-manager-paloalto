<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>NAS客户端管理</h2>
      <div>
        <el-button type="success" :loading="syncing" @click="handleSyncConfig">同步配置</el-button>
        <el-button type="primary" @click="openCreateDialog">新建客户端</el-button>
      </div>
    </div>

    <el-card shadow="never">
      <el-table :data="clients" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="shortname" label="名称" min-width="120" />
        <el-table-column prop="ip_address" label="IP地址" width="150" />
        <el-table-column prop="nas_type" label="类型" width="100" />
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'danger'" size="small">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该客户端？" @confirm="handleDelete(row.id)">
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
          @change="fetchClients"
        />
      </div>
    </el-card>

    <!-- Create/Edit Dialog -->
    <NasFormDialog
      v-model:visible="dialogVisible"
      :client="editingClient"
      @saved="fetchClients"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getNasClients, deleteNasClient, syncNasConfig } from '@/api/nas'
import NasFormDialog from './NasFormDialog.vue'

const loading = ref(false)
const syncing = ref(false)
const clients = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editingClient = ref<any>(null)

function fetchClients() {
  loading.value = true
  getNasClients({ page: page.value, page_size: pageSize.value })
    .then((res) => {
      clients.value = res.data.items
      total.value = res.data.total
    })
    .finally(() => {
      loading.value = false
    })
}

function openCreateDialog() {
  editingClient.value = null
  dialogVisible.value = true
}

function openEditDialog(client: any) {
  editingClient.value = client
  dialogVisible.value = true
}

async function handleDelete(id: number) {
  try {
    await deleteNasClient(id)
    ElMessage.success('NAS客户端已删除')
    fetchClients()
  } catch {
    // handled by interceptor
  }
}

async function handleSyncConfig() {
  syncing.value = true
  try {
    const res = await syncNasConfig()
    ElMessage.success(res.data.message)
  } catch {
    // handled by interceptor
  } finally {
    syncing.value = false
  }
}

onMounted(fetchClients)
</script>
