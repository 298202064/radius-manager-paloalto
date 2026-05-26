<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑只读网关' : '新增只读网关'"
    width="550px"
    @update:model-value="$emit('update:visible', $event)"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <el-form-item label="名称" prop="name">
        <el-input v-model="form.name" placeholder="如: 公司VPN网关" />
      </el-form-item>
      <el-form-item label="管理地址" prop="host">
        <el-input v-model="form.host" placeholder="如: 192.168.31.200" />
        <div style="color: #999; font-size: 12px; margin-top: 4px">PAN-OS 防火墙管理接口 IP 或域名</div>
      </el-form-item>
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="只读 API 用户名" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" show-password />
        <div v-if="isEdit" style="color: #999; font-size: 12px; margin-top: 4px">留空则不修改</div>
      </el-form-item>
      <el-form-item label="状态" prop="enabled">
        <el-switch v-model="form.enabled" active-text="启用" inactive-text="禁用" />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="可选备注信息" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button v-if="isEdit" type="info" :loading="testing" @click="handleTest">测试连接</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createGateway, updateGateway, testGateway } from '@/api/gateways'

const props = defineProps<{
  visible: boolean
  gateway: any
}>()

const emit = defineEmits(['update:visible', 'saved'])

const isEdit = ref(false)
const submitting = ref(false)
const testing = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  host: '',
  username: '',
  password: '',
  enabled: true,
  description: '',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  host: [{ required: true, message: '请输入管理地址', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

watch(
  () => props.gateway,
  (gw) => {
    isEdit.value = !!gw
    if (gw) {
      form.name = gw.name
      form.host = gw.host
      form.username = gw.username
      form.password = ''
      form.enabled = gw.enabled
      form.description = gw.description || ''
    } else {
      form.name = ''
      form.host = ''
      form.username = ''
      form.password = ''
      form.enabled = true
      form.description = ''
    }
  }
)

function handleClose() {
  emit('update:visible', false)
}

async function handleTest() {
  if (!props.gateway?.id) return
  testing.value = true
  try {
    const res = await testGateway(props.gateway.id)
    if (res.data.status === 'success') {
      ElMessage.success(res.data.message)
    } else {
      ElMessage.warning(res.data.message)
    }
  } finally {
    testing.value = false
  }
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      const data: any = {}
      if (form.password) data.password = form.password
      data.name = form.name
      data.host = form.host
      data.username = form.username
      data.enabled = form.enabled
      data.description = form.description || null
      await updateGateway(props.gateway.id, data)
      ElMessage.success('只读网关已更新')
    } else {
      await createGateway({
        name: form.name,
        host: form.host,
        username: form.username,
        password: form.password,
        enabled: form.enabled,
        description: form.description || undefined,
      })
      ElMessage.success('只读网关已创建')
    }
    emit('saved')
    handleClose()
  } finally {
    submitting.value = false
  }
}
</script>
