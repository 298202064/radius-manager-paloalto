<template>
  <div class="navbar">
    <div class="navbar-left">
      <el-icon class="collapse-btn" @click="$emit('toggleCollapse')" style="cursor: pointer; font-size: 20px;">
        <Fold />
      </el-icon>
      <span class="page-title">{{ pageTitle }}</span>
    </div>
    <div class="navbar-right">
      <el-dropdown @command="handleCommand">
        <span class="user-info">
          <el-icon><User /></el-icon>
          {{ authStore.username }}
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="password">
              <el-icon><Edit /></el-icon>修改密码
            </el-dropdown-item>
            <el-dropdown-item command="otp">
              <el-icon><Key /></el-icon>OTP管理
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { logout as logoutApi } from '@/api/auth'

defineEmits(['toggleCollapse'])

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const pageTitle = computed(() => (route.meta.title as string) || '')

function handleCommand(command: string) {
  if (command === 'logout') {
    const refreshToken = authStore.refreshToken
    if (refreshToken) {
      logoutApi(refreshToken).catch(() => {})
    }
    authStore.logout()
  } else if (command === 'password') {
    router.push('/self/password')
  } else if (command === 'otp') {
    router.push('/self/otp')
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}
.navbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.page-title {
  font-size: 16px;
  font-weight: 500;
}
.navbar-right {
  display: flex;
  align-items: center;
}
.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #333;
}
</style>
