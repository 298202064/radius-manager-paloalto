<template>
  <el-container style="height: 100vh">
    <el-aside :width="isCollapsed ? '64px' : '220px'" class="app-sidebar">
      <Sidebar :is-collapsed="isCollapsed" />
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <Navbar @toggle-collapse="isCollapsed = !isCollapsed" />
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'

const isCollapsed = ref(false)
</script>

<style scoped>
.app-sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}
.app-header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
  display: flex;
  align-items: center;
  height: 50px;
}
.app-main {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
