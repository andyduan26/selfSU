<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

import { useCourseStore } from '../stores/course'

const route = useRoute()
const router = useRouter()
const courseStore = useCourseStore()
const { courses, categories } = storeToRefs(courseStore)
const currentCategory = computed(() => route.query.category || '')

onMounted(() => {
  courseStore.fetchCourses(currentCategory.value)
})

function selectCategory(category) {
  router.push({ name: 'course-category', query: category ? { category } : {} })
  courseStore.fetchCourses(category)
}
</script>

<template>
  <main class="catalog-page">
    <section class="catalog-header">
      <p class="eyebrow">课程分类</p>
      <h1>{{ currentCategory || '全部课程' }}</h1>
    </section>
    <nav class="category-tabs" aria-label="课程分类">
      <button type="button" @click="selectCategory('')">全部</button>
      <button v-for="category in categories" :key="category" type="button" @click="selectCategory(category)">{{ category }}</button>
    </nav>
    <section class="course-grid catalog-grid">
      <RouterLink v-for="course in courses" :key="course.id" class="course-card" :to="`/courses/${course.id}`">
        <img v-if="course.cover" :src="course.cover" :alt="course.title">
        <div v-else class="cover-fallback">{{ course.category }}</div>
        <span class="cover-title">{{ course.title }}</span>
      </RouterLink>
    </section>
  </main>
</template>
