<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑用户' : '新建用户'"
    width="500px"
    @update:model-value="$emit('update:visible', $event)"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" :disabled="isEdit" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item label="角色" prop="role">
        <el-select v-model="form.role" style="width: 100%">
          <el-option label="普通用户" value="user" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="enabled">
        <el-switch v-model="form.enabled" active-text="启用" inactive-text="禁用" />
      </el-form-item>
      <el-form-item label="备注" prop="note">
        <el-input v-model="form.note" type="textarea" :rows="3" />
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
import { createUser, updateUser } from '@/api/users'

const props = defineProps<{
  visible: boolean
  user: any
}>()

const emit = defineEmits(['update:visible', 'saved'])

const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  username: '',
  password: '',
  email: '',
  role: 'user',
  enabled: true,
  note: '',
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 64, message: '用户名长度3-64字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
}

watch(
  () => props.user,
  (user) => {
    isEdit.value = !!user
    if (user) {
      form.username = user.username
      form.password = ''
      form.email = user.email || ''
      form.role = user.role
      form.enabled = user.enabled
      form.note = user.note || ''
      rules.password = []  // Password is optional in edit mode
    } else {
      form.username = ''
      form.password = ''
      form.email = ''
      form.role = 'user'
      form.enabled = true
      form.note = ''
      rules.password = [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码至少6位', trigger: 'blur' },
      ]
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
      if (form.password) data.password = form.password
      data.email = form.email || null
      data.role = form.role
      data.enabled = form.enabled
      data.note = form.note || null
      await updateUser(props.user.id, data)
      ElMessage.success('用户已更新')
    } else {
      await createUser({
        username: form.username,
        password: form.password,
        email: form.email || undefined,
        role: form.role,
        enabled: form.enabled,
        note: form.note || undefined,
      })
      ElMessage.success('用户已创建')
    }
    emit('saved')
    handleClose()
  } finally {
    submitting.value = false
  }
}
</script>
