<template>
  <div>
    <h2 style="margin-bottom: 20px">认证日志</h2>

    <el-card shadow="never" style="margin-bottom: 16px">
      <el-form :inline="true" :model="filter">
        <el-form-item label="用户名">
          <el-input v-model="filter.username" placeholder="搜索用户名" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="结果">
          <el-select v-model="filter.result" placeholder="全部" clearable style="width: 140px">
            <el-option label="成功" value="Access-Accept" />
            <el-option label="失败" value="Access-Reject" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker v-model="filter.startDate" type="datetime" placeholder="开始时间" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker v-model="filter.endDate" type="datetime" placeholder="结束时间" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table :data="logs" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="reply" label="结果" width="120">
          <template #default="{ row }">
            <el-tag :type="row.reply === 'Access-Accept' ? 'success' : 'danger'" size="small">
              {{ row.reply === 'Access-Accept' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="callingstationid" label="源 IP" width="150" />
        <el-table-column prop="nasipaddress" label="NAS IP" width="130" />
        <el-table-column prop="calledstationid" label="NAS/被叫方" width="150" />
        <el-table-column prop="authdate" label="认证时间" width="180" />
      </el-table>

      <div style="display: flex; justify-content: flex-end; margin-top: 16px">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @change="fetchLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getAuthLogs } from '@/api/logs'

const loading = ref(false)
const logs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)

const filter = reactive({
  username: '',
  result: '',
  startDate: null as string | null,
  endDate: null as string | null,
})

function fetchLogs() {
  loading.value = true
  const params: any = {
    page: page.value,
    page_size: pageSize.value,
    username: filter.username,
    result: filter.result,
  }
  if (filter.startDate) params.start_date = filter.startDate
  if (filter.endDate) params.end_date = filter.endDate

  getAuthLogs(params)
    .then((res) => {
      logs.value = res.data.items
      total.value = res.data.total
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearch() {
  page.value = 1
  fetchLogs()
}

function resetSearch() {
  filter.username = ''
  filter.result = ''
  filter.startDate = null
  filter.endDate = null
  handleSearch()
}

onMounted(fetchLogs)
</script>
