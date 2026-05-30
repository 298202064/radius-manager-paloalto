<template>
  <div class="login-container">
    <!-- Background floating elements -->
    <div class="bg-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <div class="login-card">
      <!-- Logo / Brand -->
      <div class="brand">
        <div class="brand-icon">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="24" cy="24" r="22" stroke="currentColor" stroke-width="2.5" fill="none"/>
            <path d="M16 24 L22 30 L32 18" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h1 class="brand-name">RADIUS Manager</h1>
        <p class="brand-desc">认证管理系统 &bull; Enterprise</p>
      </div>

      <!-- Login Form -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        size="large"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            :prefix-icon="UserIcon"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="LockIcon"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="error" class="login-error">
        <span class="error-icon">!</span>
        {{ error }}
      </div>
    </div>

    <!-- Footer -->
    <div class="login-footer">
      <span>v{{ version }}</span>
      <span class="footer-sep">|</span>
      <a href="https://forum.wangsz-lab.com" target="_blank" class="footer-link">
        问题反馈
      </a>
      <span class="footer-sep">|</span>
      <span>RADIUS Manager</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '@/api/auth'
import { useAuthStore } from '@/store/auth'

const version = '1.0.0'
const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

function UserIcon() { return h(User) }
function LockIcon() { return h(Lock) }

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  error.value = ''

  try {
    const res = await login(form.username, form.password)
    const data = res.data
    authStore.setTokens(data.access_token, data.refresh_token)
    authStore.setUser(data.user)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── Container ── */
.login-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at 30% 20%, #0d2137 0%, #0a1628 50%, #060e1a 100%);
  overflow: hidden;
}

/* ── Background shapes ── */
.bg-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}
.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.03;
}
.shape-1 {
  width: 600px; height: 600px;
  background: #0095FF;
  top: -200px; right: -100px;
  animation: float 20s ease-in-out infinite;
}
.shape-2 {
  width: 400px; height: 400px;
  background: #00D4AA;
  bottom: -100px; left: -100px;
  animation: float 25s ease-in-out infinite reverse;
}
.shape-3 {
  width: 300px; height: 300px;
  background: #0095FF;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  animation: float 30s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.05); }
  66% { transform: translate(-20px, 20px) scale(0.95); }
}

/* ── Card ── */
.login-card {
  position: relative;
  z-index: 1;
  width: 400px;
  padding: 48px 40px 40px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.4);
}

/* ── Brand ── */
.brand {
  text-align: center;
  margin-bottom: 36px;
}
.brand-icon {
  width: 52px;
  height: 52px;
  margin: 0 auto 16px;
  color: #0095FF;
}
.brand-name {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.3px;
}
.brand-desc {
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 1px;
}

/* ── Form ── */
.login-form {
  margin-bottom: 4px;
}
.login-form :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: none;
  border-radius: 10px;
  padding: 4px 16px;
  transition: border-color 0.2s, background 0.2s;
}
.login-form :deep(.el-input__wrapper:hover) {
  border-color: rgba(255, 255, 255, 0.2);
}
.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: #0095FF;
  background: rgba(255, 255, 255, 0.08);
}
.login-form :deep(.el-input__inner) {
  color: #ffffff;
  caret-color: #0095FF;
}
.login-form :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.3);
}
.login-form :deep(.el-input__prefix) {
  color: rgba(255, 255, 255, 0.3);
}
.login-form :deep(.el-input--large) {
  --el-input-height: 48px;
}
.login-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #0095FF 0%, #0066CC 100%);
  color: #fff;
  letter-spacing: 1px;
  transition: opacity 0.2s, transform 0.15s;
}
.login-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}
.login-btn:active {
  transform: translateY(0);
}
.login-btn.is-loading {
  opacity: 0.8;
}

/* ── Error ── */
.login-error {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(245, 108, 108, 0.1);
  border: 1px solid rgba(245, 108, 108, 0.2);
  border-radius: 10px;
  color: #f56c6c;
  font-size: 13px;
}
.error-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(245, 108, 108, 0.2);
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

/* ── Footer ── */
.login-footer {
  position: absolute;
  bottom: 32px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.25);
  z-index: 1;
}
.footer-sep {
  margin: 0 12px;
  opacity: 0.4;
}
.footer-link {
  color: rgba(255, 255, 255, 0.35);
  text-decoration: none;
  transition: color 0.2s;
}
.footer-link:hover {
  color: #0095FF;
}
</style>
