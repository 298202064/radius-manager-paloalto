<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>只读网关管理</h2>
      <el-button type="primary" @click="openCreateDialog">新增网关</el-button>
    </div>
    <div style="color: #909399; font-size: 13px; margin-bottom: 16px">
      配置 PAN-OS 防火墙只读账号后，系统可通过 API 自动获取 GlobalProtect VPN 在线用户信息。
    </div>

    <el-card shadow="never">
      <el-table :data="gateways" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="host" label="管理地址" width="150" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'danger'" size="small">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleTest(row)">测试</el-button>
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该网关？" @confirm="handleDelete(row.id)">
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
          @change="fetchGateways"
        />
      </div>
    </el-card>

    <GatewayFormDialog
      v-model:visible="dialogVisible"
      :gateway="editingGateway"
      @saved="fetchGateways"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getGateways, deleteGateway, testGateway } from '@/api/gateways'
import GatewayFormDialog from './GatewayFormDialog.vue'

const loading = ref(false)
const gateways = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editingGateway = ref<any>(null)

function fetchGateways() {
  loading.value = true
  getGateways({ page: page.value, page_size: pageSize.value })
    .then((res) => {
      gateways.value = res.data.items
      total.value = res.data.total
    })
    .finally(() => {
      loading.value = false
    })
}

function openCreateDialog() {
  editingGateway.value = null
  dialogVisible.value = true
}

function openEditDialog(gw: any) {
  editingGateway.value = gw
  dialogVisible.value = true
}

async function handleTest(row: any) {
  try {
    const res = await testGateway(row.id)
    if (res.data.status === 'success') {
      ElMessage.success(res.data.message)
    } else {
      ElMessage.warning(res.data.message)
    }
  } catch {
    // handled by interceptor
  }
}

async function handleDelete(id: number) {
  try {
    await deleteGateway(id)
    ElMessage.success('只读网关已删除')
    fetchGateways()
  } catch {
    // handled by interceptor
  }
}

onMounted(fetchGateways)
</script>
