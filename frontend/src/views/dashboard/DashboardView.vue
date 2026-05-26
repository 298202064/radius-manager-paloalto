<template>
  <div>
    <h2 style="margin-bottom: 20px">仪表盘</h2>

    <template v-if="isAdmin">
      <el-row :gutter="20">
        <el-col :span="4">
          <el-card shadow="hover">
            <div class="stat-card">
              <div class="stat-value">{{ stats.total_users }}</div>
              <div class="stat-label">总用户数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="5">
          <el-card shadow="hover">
            <div class="stat-card">
              <div class="stat-value" style="color: #67c23a">{{ stats.active_users_online }}</div>
              <div class="stat-label">当前在线</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="5">
          <el-card shadow="hover">
            <div class="stat-card">
              <div class="stat-value" style="color: #409eff">{{ stats.total_nas_clients }}</div>
              <div class="stat-label">NAS客户端</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="5">
          <el-card shadow="hover">
            <div class="stat-card">
              <div class="stat-value" style="color: #909399">{{ stats.total_gateways }}</div>
              <div class="stat-label">只读网关</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="5">
          <el-card shadow="hover">
            <div class="stat-card">
              <div class="stat-value" style="color: #e6a23c">{{ stats.today_auth_attempts }}</div>
              <div class="stat-label">今日认证次数</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>今日认证状况</span>
            </template>
            <div style="padding: 20px; text-align: center">
              <el-progress
                type="dashboard"
                :percentage="successRate"
                :color="successRate > 90 ? '#67c23a' : '#e6a23c'"
              >
                <template #default>
                  <span style="font-size: 24px">{{ successRate }}%</span>
                </template>
              </el-progress>
              <div style="margin-top: 16px; color: #999">
                成功 {{ stats.today_auth_success }} / 失败 {{ stats.today_auth_failures }}
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>快速入口</span>
            </template>
            <div style="display: flex; flex-wrap: wrap; gap: 12px">
              <el-button type="primary" @click="$router.push('/users')">用户管理</el-button>
              <el-button type="success" @click="$router.push('/nas-clients')">NAS客户端</el-button>
              <el-button @click="$router.push('/gateways')">只读网关</el-button>
              <el-button type="warning" @click="$router.push('/logs/auth')">认证日志</el-button>
              <el-button type="info" @click="$router.push('/logs/online')">在线用户</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <template v-else>
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card shadow="hover">
            <div style="text-align: center; padding: 40px 0">
              <h3>欢迎回来，{{ username }}</h3>
              <p style="color: #909399; margin-top: 12px">
                您可以通过左侧菜单使用自助服务
              </p>
              <div style="margin-top: 24px; display: flex; gap: 12px; justify-content: center">
                <el-button type="primary" @click="$router.push('/self/password')">修改密码</el-button>
                <el-button type="success" @click="$router.push('/self/otp')">OTP 管理</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getDashboardStats } from '@/api/logs'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const isAdmin = authStore.isAdmin
const username = authStore.username

const stats = ref({
  total_users: 0,
  active_users_online: 0,
  total_nas_clients: 0,
  total_gateways: 0,
  today_auth_attempts: 0,
  today_auth_success: 0,
  today_auth_failures: 0,
})

const successRate = computed(() => {
  if (stats.value.today_auth_attempts === 0) return 100
  return Math.round(
    (stats.value.today_auth_success / stats.value.today_auth_attempts) * 100
  )
})

onMounted(async () => {
  try {
    const res = await getDashboardStats()
    stats.value = res.data
  } catch {
    // Error handled by interceptor
  }
})
</script>

<style scoped>
.stat-card {
  text-align: center;
  padding: 10px 0;
}
.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #303133;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
</style>
