<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const { loading, error } = storeToRefs(authStore)

const form = reactive({
  username: '',
  password: '',
})

async function submitLogin() {
  await authStore.login(form)
  router.push({ name: 'profile' })
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-panel">
      <p class="eyebrow">账号登录</p>
      <h1>欢迎回来</h1>
      <form class="form" @submit.prevent="submitLogin">
        <label>
          <span>账号</span>
          <input v-model="form.username" name="username" autocomplete="username" required>
        </label>
        <label>
          <span>密码</span>
          <input v-model="form.password" name="password" type="password" autocomplete="current-password" required>
        </label>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button type="submit" :disabled="loading">{{ loading ? '登录中' : '登录' }}</button>
      </form>
      <RouterLink class="text-link" to="/register">还没有账号，去注册</RouterLink>
    </section>
  </main>
</template>
