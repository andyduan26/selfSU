<script setup>
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'

import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const { teacherStatus } = storeToRefs(authStore)
const isTeacher = computed(() => teacherStatus.value?.is_teacher)
const applicationStatus = computed(() => teacherStatus.value?.application_status)

onMounted(() => {
  authStore.fetchTeacherStatus()
})
</script>

<template>
  <main class="profile-page">
    <section class="profile-header">
      <p class="eyebrow">教师中心</p>
      <h1>{{ isTeacher ? '课程创作中心' : '抱歉，请先申请认证教师。' }}</h1>
    </section>

    <section v-if="isTeacher" class="teacher-panel">
      <p>认证通过后，可在这里继续建设课程、章节、小节和收益管理能力。</p>
    </section>

    <section v-else class="teacher-panel">
      <p v-if="applicationStatus === 'pending'">当前认证状态：待审核。耐心等待2-3个工作日，结果会邮箱通知。</p>
      <p v-else-if="applicationStatus === 'rejected'">当前认证状态：未通过。请修改资料后重新申请。</p>
      <p v-else>成为认证教师后，才能进入教师中心。</p>
      <RouterLink class="text-link" to="/teacher/apply">申请认证教师</RouterLink>
    </section>
  </main>
</template>
