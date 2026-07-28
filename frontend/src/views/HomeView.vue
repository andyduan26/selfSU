<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'

import { useCourseStore } from '../stores/course'
import { useSystemStore } from '../stores/system'

const systemStore = useSystemStore()
const courseStore = useCourseStore()
const { health, loading, error } = storeToRefs(systemStore)
const { courses } = storeToRefs(courseStore)

onMounted(() => {
  systemStore.fetchHealth()
  courseStore.fetchCourses()
})
</script>

<template>
  <main class="home-page">
    <section class="intro">
      <p class="eyebrow">东方知识库</p>
      <h1>知识分享与视频课程平台</h1>
      <p class="summary">面向普通用户、认证教师和管理员，逐步建设课程内容、教师认证、支付和视频学习闭环。</p>
      <nav class="actions" aria-label="账户入口">
        <RouterLink to="/register">注册</RouterLink>
        <RouterLink to="/login">登录</RouterLink>
        <RouterLink to="/profile">个人中心</RouterLink>
        <RouterLink to="/teacher">教师中心</RouterLink>
        <RouterLink to="/courses">全部课程</RouterLink>
      </nav>
    </section>

    <section class="status-panel" aria-label="系统状态">
      <span class="label">API 状态</span>
      <strong v-if="loading">检查中</strong>
      <strong v-else-if="error" class="error">{{ error }}</strong>
      <strong v-else>{{ health?.status || '未连接' }}</strong>
      <small>{{ health?.service || '等待后端响应' }}</small>
    </section>

    <section class="course-band">
      <div class="section-heading">
        <p class="eyebrow">课程推荐</p>
        <h2>审核通过的精选课程</h2>
      </div>
      <div class="course-grid">
        <RouterLink v-for="course in courses.slice(0, 6)" :key="course.id" class="course-card" :to="`/courses/${course.id}`">
          <img v-if="course.cover" :src="course.cover" :alt="course.title">
          <div v-else class="cover-fallback">{{ course.category }}</div>
          <span class="favorite-badge">{{ course.is_favorited ? '已收藏' : `${course.favorite_count || 0} 收藏` }}</span>
          <span class="cover-title">{{ course.title }}</span>
        </RouterLink>
      </div>
    </section>
  </main>
</template>
