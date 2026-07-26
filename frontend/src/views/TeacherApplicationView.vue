<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const { user, loading, error } = storeToRefs(authStore)
const notice = ref('')

const form = reactive({
  real_name: user.value?.nickname || '',
  phone: user.value?.phone || '',
  email: user.value?.email || '',
  bio: '',
})

async function submitApplication() {
  const data = await authStore.submitTeacherApplication(form)
  notice.value = data.notice
  window.alert(data.notice)
  router.push({ name: 'teacher-center' })
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-panel">
      <p class="eyebrow">教师认证</p>
      <h1>申请成为认证教师</h1>
      <p v-if="notice" class="notice">{{ notice }}</p>
      <form class="form" @submit.prevent="submitApplication">
        <label>
          <span>真实姓名</span>
          <input v-model="form.real_name" required>
        </label>
        <label>
          <span>联系电话</span>
          <input v-model="form.phone" required>
        </label>
        <label>
          <span>联系邮箱</span>
          <input v-model="form.email" type="email" required>
        </label>
        <label>
          <span>申请说明</span>
          <textarea v-model="form.bio" rows="5" required />
        </label>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button type="submit" :disabled="loading">{{ loading ? '提交中' : '提交申请' }}</button>
      </form>
    </section>
  </main>
</template>
