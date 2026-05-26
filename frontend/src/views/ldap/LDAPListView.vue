<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>只读 LDAP</h2>
      <el-button type="primary" @click="openCreate">新增服务器</el-button>
    </div>
    <div style="color: #909399; font-size: 13px; margin-bottom: 16px">
      配置 Active Directory LDAP 服务器，搜索并导入 AD 用户到本系统。导入的用户将获得随机初始密码，
      可在用户管理中绑定 OTP，用户也可在自助服务页面修改密码。
    </div>

    <el-card shadow="never">
      <el-table :data="configs" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="host" label="主机" width="160" />
        <el-table-column prop="port" label="端口" width="70" />
        <el-table-column prop="base_dn" label="Base DN" min-width="200" show-overflow-tooltip />
        <el-table-column prop="bind_dn" label="Bind DN" min-width="200" show-overflow-tooltip />
        <el-table-column prop="use_tls" label="TLS" width="70">
          <template #default="{ row }">
            <el-tag :type="row.use_tls ? 'success' : 'info'" size="small">
              {{ row.use_tls ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'danger'" size="small">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleTest(row)">测试</el-button>
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="success" @click="openImport(row)">导入用户</el-button>
            <el-popconfirm title="确定删除该配置？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && configs.length === 0" style="text-align: center; padding: 40px; color: #909399">
        <p>暂无 LDAP 服务器配置</p>
        <p style="font-size: 12px; margin-top: 8px">
          点击「新增服务器」添加 Active Directory 连接配置
        </p>
      </div>

      <div style="margin-top: 16px; text-align: right">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @change="fetchConfigs"
        />
      </div>
    </el-card>

    <LDAPFormDialog v-model:visible="dialogVisible" :config="editingConfig" @saved="fetchConfigs" />
    <LDAPImportDialog v-model:visible="importDialogVisible" :config-id="importConfigId" @imported="fetchConfigs" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getLDAPConfigs, deleteLDAPConfig, testLDAPConnection } from '@/api/ldap'
import LDAPFormDialog from './LDAPFormDialog.vue'
import LDAPImportDialog from './LDAPImportDialog.vue'

const loading = ref(false)
const configs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editingConfig = ref<any>(null)
const importDialogVisible = ref(false)
const importConfigId = ref(0)

async function fetchConfigs() {
  loading.value = true
  try {
    const res = await getLDAPConfigs({ page: page.value, page_size: pageSize.value })
    configs.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingConfig.value = null
  dialogVisible.value = true
}

function openEdit(row: any) {
  editingConfig.value = row
  dialogVisible.value = true
}

function openImport(row: any) {
  importConfigId.value = row.id
  importDialogVisible.value = true
}

async function handleTest(row: any) {
  try {
    const res = await testLDAPConnection(row.id)
    if (res.data.status === 'success') {
      ElMessage.success(res.data.message)
    } else {
      ElMessage.error(res.data.message)
    }
  } catch {
    // handled by interceptor
  }
}

async function handleDelete(row: any) {
  try {
    await deleteLDAPConfig(row.id)
    ElMessage.success('已删除')
    await fetchConfigs()
  } catch {
    // handled by interceptor
  }
}

onMounted(fetchConfigs)
</script>
