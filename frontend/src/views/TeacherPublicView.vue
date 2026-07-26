<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'

import { useCourseStore } from '../stores/course'

const route = useRoute()
const courseStore = useCourseStore()
const { currentTeacher } = storeToRefs(courseStore)

onMounted(() => {
  courseStore.fetchTeacher(route.params.id)
})
</script>

<template>
  <main v-if="currentTeacher" class="catalog-page">
    <section class="catalog-header">
      <p class="eyebrow">教师主页</p>
      <h1>{{ currentTeacher.display_name }}</h1>
      <p class="summary">{{ currentTeacher.bio || currentTeacher.title }}</p>
    </section>
    <section class="course-grid catalog-grid">
      <RouterLink v-for="course in currentTeacher.courses" :key="course.id" class="course-card" :to="`/courses/${course.id}`">
        <img v-if="course.cover" :src="course.cover" :alt="course.title">
        <div v-else class="cover-fallback">{{ course.category }}</div>
        <span class="cover-title">{{ course.title }}</span>
      </RouterLink>
    </section>
  </main>
</template>
