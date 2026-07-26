<script setup>
import { reactive, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const { user, loading, error } = storeToRefs(authStore)

const form = reactive({
  nickname: '',
  email: '',
  phone: '',
})

watchEffect(() => {
  if (user.value) {
    form.nickname = user.value.nickname || ''
    form.email = user.value.email || ''
    form.phone = user.value.phone || ''
  }
})

authStore.fetchMe()

async function submitProfile() {
  await authStore.updateProfile(form)
}

function logout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <main class="profile-page">
    <section class="profile-header">
      <p class="eyebrow">个人中心</p>
      <h1>{{ user?.nickname || '用户资料' }}</h1>
      <button type="button" class="secondary-button" @click="logout">退出登录</button>
    </section>

    <section v-if="user" class="profile-grid">
      <dl class="profile-details">
        <div>
          <dt>账号</dt>
          <dd>{{ user.username }}</dd>
        </div>
        <div>
          <dt>昵称</dt>
          <dd>{{ user.nickname }}</dd>
        </div>
        <div>
          <dt>邮箱</dt>
          <dd>{{ user.email }}</dd>
        </div>
        <div>
          <dt>手机号</dt>
          <dd>{{ user.phone }}</dd>
        </div>
        <div>
          <dt>注册时间</dt>
          <dd>{{ new Date(user.registered_at).toLocaleString('zh-CN') }}</dd>
        </div>
      </dl>

      <form class="form" @submit.prevent="submitProfile">
        <label>
          <span>昵称</span>
          <input v-model="form.nickname" name="nickname" required>
        </label>
        <label>
          <span>邮箱</span>
          <input v-model="form.email" name="email" type="email" required>
        </label>
        <label>
          <span>手机号</span>
          <input v-model="form.phone" name="phone" required>
        </label>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button type="submit" :disabled="loading">{{ loading ? '保存中' : '保存资料' }}</button>
      </form>
    </section>
  </main>
</template>
