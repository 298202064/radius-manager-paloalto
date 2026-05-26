<template>
  <div>
    <h2 style="margin-bottom: 20px">在线用户</h2>

    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>VPN 网关在线用户</span>
          <el-button size="small" type="primary" :loading="loading" @click="fetchUsers">
            刷新
          </el-button>
        </div>
      </template>
      <el-table :data="users" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="gateway_name" label="网关" width="120" />
        <el-table-column prop="username" label="用户名" min-width="160" />
        <el-table-column prop="computer" label="计算机名" width="140" />
        <el-table-column prop="client_os" label="客户端" min-width="180" />
        <el-table-column prop="virtual_ip" label="VPN IP" width="130" />
        <el-table-column prop="public_ip" label="公网 IP" width="130" />
        <el-table-column prop="login_time" label="上线时间" width="160" />
        <el-table-column prop="tunnel_type" label="隧道类型" width="100" />
      </el-table>

      <div v-if="!loading && users.length === 0" style="text-align: center; padding: 40px; color: #909399">
        <p>暂无在线用户</p>
        <p style="font-size: 12px; margin-top: 8px">
          请先在「只读网关」中添加并启用 PAN-OS 防火墙网关
        </p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getGatewayOnlineUsers } from '@/api/gateways'

const loading = ref(false)
const users = ref<any[]>([])

async function fetchUsers() {
  loading.value = true
  try {
    const res = await getGatewayOnlineUsers()
    users.value = res.data.items
  } finally {
    loading.value = false
  }
}

onMounted(fetchUsers)
</script>
