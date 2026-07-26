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
  nickname: '',
  email: '',
  phone: '',
  password: '',
})

async function submitRegister() {
  await authStore.register(form)
  router.push({ name: 'profile' })
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-panel">
      <p class="eyebrow">创建账号</p>
      <h1>加入东方知识库</h1>
      <form class="form" @submit.prevent="submitRegister">
        <label>
          <span>账号</span>
          <input v-model="form.username" name="username" autocomplete="username" required>
        </label>
        <label>
          <span>昵称</span>
          <input v-model="form.nickname" name="nickname" required>
        </label>
        <label>
          <span>邮箱</span>
          <input v-model="form.email" name="email" type="email" autocomplete="email" required>
        </label>
        <label>
          <span>手机号</span>
          <input v-model="form.phone" name="phone" autocomplete="tel" required>
        </label>
        <label>
          <span>密码</span>
          <input v-model="form.password" name="password" type="password" autocomplete="new-password" minlength="8" required>
        </label>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button type="submit" :disabled="loading">{{ loading ? '注册中' : '注册' }}</button>
      </form>
      <RouterLink class="text-link" to="/login">已有账号，去登录</RouterLink>
    </section>
  </main>
</template>
