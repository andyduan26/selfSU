<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'

import { useCourseStore } from '../stores/course'

const route = useRoute()
const courseStore = useCourseStore()
const { currentLesson } = storeToRefs(courseStore)
const error = ref('')

onMounted(async () => {
  try {
    await courseStore.fetchLessonPlay(route.params.id)
  } catch (requestError) {
    error.value = requestError.response?.data?.message || '未购买课程只能试看'
  }
})
</script>

<template>
  <main class="player-page">
    <section v-if="currentLesson" class="player-panel">
      <p class="eyebrow">视频播放</p>
      <h1>{{ currentLesson.title }}</h1>
      <video v-if="currentLesson.hls_url || currentLesson.video_file" :src="currentLesson.hls_url || currentLesson.video_file" controls />
      <p v-else class="summary">视频文件正在准备中。</p>
    </section>
    <section v-else class="player-panel">
      <p class="eyebrow">播放权限</p>
      <h1>{{ error || '正在加载' }}</h1>
    </section>
  </main>
</template>
