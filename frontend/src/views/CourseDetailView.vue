<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'

import { useCourseStore } from '../stores/course'

const route = useRoute()
const courseStore = useCourseStore()
const { currentCourse } = storeToRefs(courseStore)
const orderMessage = ref('')

onMounted(() => {
  courseStore.fetchCourse(route.params.id)
})

async function buyCourse() {
  const order = await courseStore.createCourseOrder(route.params.id)
  orderMessage.value = order.pay_status === 'paid'
    ? '课程已开通，可以播放完整内容。'
    : `订单已创建，订单号：${order.order_no}。请完成支付后观看完整课程。`
  await courseStore.fetchCourse(route.params.id)
}
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
        <button type="button" class="buy-button" @click="buyCourse">购买课程</button>
        <p v-if="orderMessage" class="notice">{{ orderMessage }}</p>
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
