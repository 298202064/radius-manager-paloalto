<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑LDAP服务器' : '新增LDAP服务器'"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" @keyup.enter="handleSave">
      <el-form-item label="名称" prop="name">
        <el-input v-model="form.name" placeholder="例如: 公司AD" />
      </el-form-item>
      <el-row :gutter="10">
        <el-col :span="16">
          <el-form-item label="主机地址" prop="host">
            <el-input v-model="form.host" placeholder="IP 或 FQDN" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="端口" prop="port">
            <el-input-number v-model="form.port" :min="1" :max="65535" :controls="false" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Base DN" prop="base_dn">
        <el-input v-model="form.base_dn" placeholder="例如: DC=company,DC=com" />
      </el-form-item>
      <el-form-item label="Bind DN" prop="bind_dn">
        <el-input v-model="form.bind_dn" placeholder="例如: CN=reader,CN=Users,DC=company,DC=com" />
      </el-form-item>
      <el-form-item label="Bind 密码" prop="bind_password">
        <el-input v-model="form.bind_password" type="password" show-password
          :placeholder="isEdit ? '留空则不修改' : '请输入密码'" />
      </el-form-item>
      <el-form-item label="使用 TLS">
        <el-switch v-model="form.use_tls" />
        <span style="margin-left: 8px; font-size: 12px; color: #909399">
          {{ form.use_tls ? 'LDAPS (端口 636)' : 'LDAP (端口 389)' }}
        </span>
      </el-form-item>
      <el-form-item label="启用">
        <el-switch v-model="form.enabled" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button v-if="isEdit" :loading="testing" @click="handleTest">测试连接</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createLDAPConfig, updateLDAPConfig, testLDAPConnection } from '@/api/ldap'

const props = defineProps<{ visible: boolean; config: any }>()
const emit = defineEmits(['update:visible', 'saved'])

const isEdit = ref(false)
const submitting = ref(false)
const testing = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  host: '',
  port: 389,
  base_dn: '',
  bind_dn: '',
  bind_password: '',
  use_tls: false,
  enabled: true,
  description: '',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  base_dn: [{ required: true, message: '请输入 Base DN', trigger: 'blur' }],
  bind_dn: [{ required: true, message: '请输入 Bind DN', trigger: 'blur' }],
}

watch(() => props.config, (val) => {
  if (val && val.id) {
    isEdit.value = true
    form.name = val.name
    form.host = val.host
    form.port = val.port
    form.base_dn = val.base_dn
    form.bind_dn = val.bind_dn
    form.bind_password = ''
    form.use_tls = val.use_tls
    form.enabled = val.enabled
    form.description = val.description || ''
  } else {
    isEdit.value = false
    form.name = ''
    form.host = ''
    form.port = 389
    form.base_dn = ''
    form.bind_dn = ''
    form.bind_password = ''
    form.use_tls = false
    form.enabled = true
    form.description = ''
  }
}, { immediate: true })

function handleClose() {
  emit('update:visible', false)
}

async function handleTest() {
  if (!props.config?.id) return
  testing.value = true
  try {
    const res = await testLDAPConnection(props.config.id)
    if (res.data.status === 'success') {
      ElMessage.success(res.data.message)
    } else {
      ElMessage.error(res.data.message)
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
      const data: any = {
        name: form.name,
        host: form.host,
        port: form.port,
        base_dn: form.base_dn,
        bind_dn: form.bind_dn,
        use_tls: form.use_tls,
        enabled: form.enabled,
        description: form.description || undefined,
      }
      if (form.bind_password) {
        data.bind_password = form.bind_password
      }
      await updateLDAPConfig(props.config.id, data)
      ElMessage.success('更新成功')
    } else {
      await createLDAPConfig({
        name: form.name,
        host: form.host,
        port: form.port,
        base_dn: form.base_dn,
        bind_dn: form.bind_dn,
        bind_password: form.bind_password,
        use_tls: form.use_tls,
        enabled: form.enabled,
        description: form.description || undefined,
      })
      ElMessage.success('创建成功')
    }
    emit('saved')
    handleClose()
  } finally {
    submitting.value = false
  }
}
</script>
