<template>
  <div>
    <h2 style="margin-bottom: 20px">OTP管理</h2>

    <el-row :gutter="20">
      <!-- Binding Status -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span>OTP绑定状态</span>
          </template>
          <div v-loading="statusLoading">
            <p v-if="otpStatus === null">请点击"检查状态"</p>
            <div v-else>
              <p>
                状态:
                <el-tag :type="otpStatus.enabled ? 'success' : 'info'" size="small">
                  {{ otpStatus.enabled ? '已绑定' : '未绑定' }}
                </el-tag>
              </p>
              <p v-if="otpStatus.enabled">
                设备: {{ otpStatus.device_name }}
              </p>
              <div style="margin-top: 16px">
                <el-button @click="checkStatus">检查状态</el-button>
                <el-button
                  v-if="otpStatus.enabled"
                  type="danger"
                  @click="handleUnbind"
                  :loading="unbinding"
                >
                  解除绑定
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Bind New Device -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span>绑定新设备</span>
          </template>

          <el-steps :active="bindStep" simple style="margin-bottom: 20px">
            <el-step title="获取二维码" />
            <el-step title="验证绑定" />
          </el-steps>

          <div v-if="bindStep === 0">
            <el-button type="primary" @click="handleGetQrcode" :loading="qrcodeLoading">
              获取二维码
            </el-button>

            <div v-if="qrcodeData" style="margin-top: 16px; text-align: center">
              <img :src="'data:image/png;base64,' + qrcodeData.qrcode" alt="OTP QR Code" style="width: 200px; height: 200px" />
              <p style="color: #999; font-size: 12px; margin-top: 8px">
                请使用 Google Authenticator 或 Authy 扫描二维码
              </p>
              <el-button style="margin-top: 8px" @click="bindStep = 1">我已扫描，下一步</el-button>
            </div>
          </div>

          <div v-if="bindStep === 1">
            <el-form ref="bindFormRef" :model="bindForm" :rules="bindRules">
              <el-form-item label="验证码" prop="token">
                <el-input
                  v-model="bindForm.token"
                  placeholder="输入App中的6位验证码"
                  maxlength="6"
                  style="width: 220px"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleBind" :loading="bindLoading">确认绑定</el-button>
                <el-button @click="bindStep = 0">返回</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getOtpStatus, getOtpQrcode, bindOtp, unbindOtp } from '@/api/self'

const statusLoading = ref(false)
const otpStatus = ref<any>(null)
const qrcodeLoading = ref(false)
const qrcodeData = ref<any>(null)
const bindLoading = ref(false)
const unbinding = ref(false)
const bindStep = ref(0)
const bindFormRef = ref<FormInstance>()

const bindForm = reactive({
  token: '',
})

const bindRules: FormRules = {
  token: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' },
  ],
}

async function checkStatus() {
  statusLoading.value = true
  try {
    const res = await getOtpStatus()
    otpStatus.value = res.data
  } finally {
    statusLoading.value = false
  }
}

async function handleGetQrcode() {
  qrcodeLoading.value = true
  try {
    const res = await getOtpQrcode()
    qrcodeData.value = res.data
  } finally {
    qrcodeLoading.value = false
  }
}

async function handleBind() {
  const valid = await bindFormRef.value?.validate().catch(() => false)
  if (!valid) return

  bindLoading.value = true
  try {
    await bindOtp(bindForm.token)
    ElMessage.success('OTP绑定成功')
    bindStep.value = 0
    qrcodeData.value = null
    bindForm.token = ''
    checkStatus()
  } finally {
    bindLoading.value = false
  }
}

async function handleUnbind() {
  try {
    await ElMessageBox.confirm('确定解除OTP绑定？', '确认')
    unbinding.value = true
    await unbindOtp()
    ElMessage.success('OTP已解除绑定')
    otpStatus.value = null
    checkStatus()
  } catch {
    // cancelled or error
  } finally {
    unbinding.value = false
  }
}
</script>
