<template>
  <div class="sidebar-wrapper">
    <div class="logo">
      <span v-if="!isCollapsed" class="logo-text">RADIUS 管理</span>
      <span v-else class="logo-text-small">R</span>
    </div>
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapsed"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <el-menu-item index="/dashboard">
        <el-icon><DataAnalysis /></el-icon>
        <span>仪表盘</span>
      </el-menu-item>

      <el-menu-item index="/users" v-if="authStore.isAdmin">
        <el-icon><User /></el-icon>
        <span>用户管理</span>
      </el-menu-item>

      <el-menu-item index="/nas-clients" v-if="authStore.isAdmin">
        <el-icon><Monitor /></el-icon>
        <span>NAS客户端</span>
      </el-menu-item>

      <el-menu-item index="/gateways" v-if="authStore.isAdmin">
        <el-icon><Connection /></el-icon>
        <span>只读网关</span>
      </el-menu-item>

      <el-menu-item index="/ldap" v-if="authStore.isAdmin">
        <el-icon><Link /></el-icon>
        <span>只读LDAP</span>
      </el-menu-item>

      <el-menu-item index="/logs/auth" v-if="authStore.isAdmin">
        <el-icon><Document /></el-icon>
        <span>认证日志</span>
      </el-menu-item>

      <el-menu-item index="/logs/online" v-if="authStore.isAdmin">
        <el-icon><Connection /></el-icon>
        <span>在线用户</span>
      </el-menu-item>

      <el-sub-menu index="self">
        <template #title>
          <el-icon><Tools /></el-icon>
          <span>自助服务</span>
        </template>
        <el-menu-item index="/self/password">
          <el-icon><Edit /></el-icon>
          <span>修改密码</span>
        </el-menu-item>
        <el-menu-item index="/self/otp">
          <el-icon><Key /></el-icon>
          <span>OTP管理</span>
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'

defineProps<{ isCollapsed: boolean }>()

const route = useRoute()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)
</script>

<style scoped>
.sidebar-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.logo {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.logo-text-small {
  font-size: 22px;
}
.el-menu {
  border-right: none;
}
</style>
