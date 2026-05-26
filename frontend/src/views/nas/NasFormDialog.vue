<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑NAS客户端' : '新建NAS客户端'"
    width="550px"
    @update:model-value="$emit('update:visible', $event)"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="名称" prop="shortname">
        <el-input v-model="form.shortname" placeholder="如: office-router" />
      </el-form-item>
      <el-form-item label="IP地址" prop="ip_address">
        <el-input v-model="form.ip_address" placeholder="如: 192.168.1.0/24" />
      </el-form-item>
      <el-form-item label="共享密钥" prop="secret">
        <el-input v-model="form.secret" type="password" show-password />
        <div v-if="isEdit" style="color: #999; font-size: 12px; margin-top: 4px">留空则不修改</div>
      </el-form-item>
      <el-form-item label="类型" prop="nas_type">
        <el-select v-model="form.nas_type" style="width: 100%">
          <el-option label="other" value="other" />
          <el-option label="cisco" value="cisco" />
          <el-option label="mikrotik" value="mikrotik" />
          <el-option label="huawei" value="huawei" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="enabled">
        <el-switch v-model="form.enabled" active-text="启用" inactive-text="禁用" />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="3" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createNasClient, updateNasClient } from '@/api/nas'

const props = defineProps<{
  visible: boolean
  client: any
}>()

const emit = defineEmits(['update:visible', 'saved'])

const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  shortname: '',
  ip_address: '',
  secret: '',
  nas_type: 'other',
  enabled: true,
  description: '',
})

const rules: FormRules = {
  shortname: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  ip_address: [{ required: true, message: '请输入IP地址', trigger: 'blur' }],
  secret: [{ required: true, message: '请输入共享密钥', trigger: 'blur' }],
}

watch(
  () => props.client,
  (client) => {
    isEdit.value = !!client
    if (client) {
      form.shortname = client.shortname
      form.ip_address = client.ip_address
      form.secret = ''
      form.nas_type = client.nas_type
      form.enabled = client.enabled
      form.description = client.description || ''
    } else {
      form.shortname = ''
      form.ip_address = ''
      form.secret = ''
      form.nas_type = 'other'
      form.enabled = true
      form.description = ''
    }
  }
)

function handleClose() {
  emit('update:visible', false)
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      const data: any = {}
      if (form.secret) data.secret = form.secret
      data.shortname = form.shortname
      data.ip_address = form.ip_address
      data.nas_type = form.nas_type
      data.enabled = form.enabled
      data.description = form.description || null
      await updateNasClient(props.client.id, data)
      ElMessage.success('NAS客户端已更新')
    } else {
      await createNasClient({
        shortname: form.shortname,
        ip_address: form.ip_address,
        secret: form.secret,
        nas_type: form.nas_type,
        enabled: form.enabled,
        description: form.description || undefined,
      })
      ElMessage.success('NAS客户端已创建')
    }
    emit('saved')
    handleClose()
  } finally {
    submitting.value = false
  }
}
</script>
