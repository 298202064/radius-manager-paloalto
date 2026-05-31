<template>
  <div>
    <h2>动态列表</h2>
    <div style="color: #909399; font-size: 13px; margin-bottom: 16px">
      管理 PA 防火墙外部动态列表（EDL）内容。编辑后保存，防火墙将在下一次拉取周期自动同步。
    </div>

    <el-card shadow="never">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="IP 地址列表" name="ip">
          <template #label>
            <span><el-icon><Monitor /></el-icon> IP 地址列表</span>
          </template>

          <div style="margin-bottom: 12px; display: flex; gap: 12px; align-items: center">
            <el-button type="primary" :loading="saving" @click="handleSaveIP">
              保存 IP 列表
            </el-button>
            <el-tag type="info" effect="plain">
              防火墙 EDL 地址: http://192.168.3.12:8081/dynamic/ip-list.txt
            </el-tag>
          </div>

          <div style="margin-bottom: 8px; color: #909399; font-size: 12px">
            每行一个 IP 地址或 CIDR 网段。例如：
            <code style="margin-left: 8px">10.0.0.1</code>
            <code style="margin-left: 4px">192.168.1.0/24</code>
          </div>

          <el-input
            v-model="ipText"
            type="textarea"
            :rows="12"
            placeholder="每行一个 IP 地址或 CIDR"
          />
        </el-tab-pane>

        <el-tab-pane label="URL 列表" name="url">
          <template #label>
            <span><el-icon><Link /></el-icon> URL 列表</span>
          </template>

          <div style="margin-bottom: 12px; display: flex; gap: 12px; align-items: center">
            <el-button type="primary" :loading="saving" @click="handleSaveURL">
              保存 URL 列表
            </el-button>
            <el-tag type="info" effect="plain">
              防火墙 EDL 地址: http://192.168.3.12:8081/dynamic/url-list.txt
            </el-tag>
          </div>

          <div style="margin-bottom: 8px; color: #909399; font-size: 12px">
            每行一个域名。防火墙规则：
            <el-popover placement="bottom" :width="360" trigger="click">
              <template #reference>
                <el-button link size="small" style="font-size: 12px">
                  域名格式说明
                  <el-icon><InfoFilled /></el-icon>
                </el-button>
              </template>
              <div style="font-size: 12px; line-height: 1.8">
                <p>防火墙会自动为不以 <code>/</code> 或 <code>*</code> 结尾的域名添加尾部斜杠。</p>
                <p><strong>示例：</strong></p>
                <ul style="padding-left: 16px">
                  <li><code>example.com</code> → 自动变 <code>example.com/</code>（匹配 example.com 及其子目录）</li>
                  <li><code>example.com/</code> → 明确指定，不会自动追加</li>
                  <li><code>*.example.com</code> → 通配符，匹配所有子域名</li>
                  <li><code>example.com*</code> → 匹配 example.com 下的所有 URL 路径</li>
                </ul>
                <p style="margin-top: 8px">推荐手动为域名添加尾部斜杠，例如 <code>example.com/</code></p>
              </div>
            </el-popover>
          </div>

          <el-input
            v-model="urlText"
            type="textarea"
            :rows="12"
            placeholder="每行一个域名，例如：&#10;baidu.com/&#10;*.google.com"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Monitor, Link, InfoFilled } from '@element-plus/icons-vue'
import { getIPList, updateIPList, getURLList, updateURLList } from '@/api/dynamicLists'

const activeTab = ref('ip')
const ipText = ref('')
const urlText = ref('')
const saving = ref(false)

async function loadIP() {
  try {
    const res = await getIPList()
    ipText.value = res.data.lines.join('\n')
  } catch {
    // handled by interceptor
  }
}

async function loadURL() {
  try {
    const res = await getURLList()
    urlText.value = res.data.lines.join('\n')
  } catch {
    // handled by interceptor
  }
}

function handleTabChange() {
  // Triggered when tab changes - content already loaded
}

async function handleSaveIP() {
  saving.value = true
  try {
    const lines = ipText.value
      .split('\n')
      .map(l => l.trim())
      .filter(l => l && !l.startsWith('#'))
    await updateIPList(lines)
    ElMessage.success(`IP 列表已保存（${lines.length} 条）`)
  } finally {
    saving.value = false
  }
}

async function handleSaveURL() {
  saving.value = true
  try {
    const lines = urlText.value
      .split('\n')
      .map(l => l.trim())
      .filter(l => l && !l.startsWith('#'))
    await updateURLList(lines)
    ElMessage.success(`URL 列表已保存（${lines.length} 条）`)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadIP()
  loadURL()
})
</script>
