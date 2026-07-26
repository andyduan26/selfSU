<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'

import { useCourseStore } from '../stores/course'

const route = useRoute()
const courseStore = useCourseStore()
const { currentCourse } = storeToRefs(courseStore)

onMounted(() => {
  courseStore.fetchCourse(route.params.id)
})
</script>

<template>
  <main v-if="currentCourse" class="detail-page">
    <section class="detail-hero">
      <img v-if="currentCourse.cover" :src="currentCourse.cover" :alt="currentCourse.title">
      <div v-else class="cover-fallback">{{ currentCourse.category }}</div>
      <div>
        <p class="eyebrow">{{ currentCourse.category }}</p>
        <h1>{{ currentCourse.title }}</h1>
        <p class="summary">{{ currentCourse.summary }}</p>
        <p class="price">¥ {{ currentCourse.price }}</p>
        <RouterLink class="text-link" :to="`/teachers/${currentCourse.teacher.id}`">讲师：{{ currentCourse.teacher.display_name }}</RouterLink>
      </div>
    </section>
    <section class="lesson-list">
      <h2>课程目录</h2>
      <article v-for="chapter in currentCourse.chapters" :key="chapter.id" class="chapter-block">
        <h3>{{ chapter.title }}</h3>
        <div v-for="lesson in chapter.lessons" :key="lesson.id" class="lesson-row">
          <span>{{ lesson.title }} <small v-if="lesson.is_trial">试看</small></span>
          <RouterLink class="inline-button" :to="`/lessons/${lesson.id}/play`">{{ lesson.can_play ? '播放' : '试看' }}</RouterLink>
        </div>
      </article>
    </section>
  </main>
</template>
