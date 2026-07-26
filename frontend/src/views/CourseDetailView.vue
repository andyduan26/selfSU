<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import QRCode from 'qrcode'

import { useCourseStore } from '../stores/course'

const route = useRoute()
const router = useRouter()
const courseStore = useCourseStore()
const { currentCourse } = storeToRefs(courseStore)
const orderMessage = ref('')
const payError = ref('')
const qrImage = ref('')
const activeOrder = ref(null)
const showPayModal = ref(false)
let pollTimer = null

onMounted(() => {
  courseStore.fetchCourse(route.params.id)
})

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function pollOrderStatus(orderNo) {
  try {
    const order = await courseStore.fetchOrderStatus(orderNo)
    activeOrder.value = order
    if (order.pay_status === 'paid') {
      stopPolling()
      showPayModal.value = false
      await courseStore.fetchCourse(route.params.id)
      const firstPlayableLesson = currentCourse.value?.chapters
        ?.flatMap((chapter) => chapter.lessons)
        ?.find((lesson) => lesson.can_play)
      if (firstPlayableLesson) {
        router.push(`/lessons/${firstPlayableLesson.id}/play`)
      }
    } else if (order.pay_status === 'closed' || order.pay_status === 'refunded') {
      stopPolling()
      payError.value = '支付失败或订单已关闭，请重新下单。'
    }
  } catch (error) {
    stopPolling()
    payError.value = error.response?.data?.message || '订单状态查询失败，请刷新后重试。'
  }
}

async function buyCourse() {
  payError.value = ''
  orderMessage.value = ''
  try {
    const order = await courseStore.createCourseOrder(route.params.id, 'alipay')
    activeOrder.value = order
    if (order.pay_status === 'paid') {
      orderMessage.value = '课程已开通，可以播放完整内容。'
      await courseStore.fetchCourse(route.params.id)
      return
    }
    const payload = await courseStore.createAlipayQrCode(order.order_no)
    if (!payload.qr_code) {
      throw new Error('后端未返回 qr_code')
    }
    qrImage.value = await QRCode.toDataURL(payload.qr_code, { width: 240, margin: 1 })
    showPayModal.value = true
    stopPolling()
    pollTimer = setInterval(() => pollOrderStatus(order.order_no), 3000)
    orderMessage.value = `订单已创建，订单号：${order.order_no}。请完成支付后观看完整课程。`
  } catch (error) {
    payError.value = error.response?.data?.message || error.message || '支付宝支付创建失败'
  }
}

onUnmounted(stopPolling)
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
        <button type="button" class="buy-button" @click="buyCourse">支付宝扫码支付</button>
        <p v-if="orderMessage" class="notice">{{ orderMessage }}</p>
        <p v-if="payError" class="form-error">{{ payError }}</p>
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

    <section v-if="showPayModal" class="pay-modal" aria-label="支付宝支付二维码">
      <div class="pay-dialog">
        <button type="button" class="inline-button close-button" @click="showPayModal = false; stopPolling()">关闭</button>
        <p class="eyebrow">支付宝扫码支付</p>
        <h2>请使用支付宝扫码</h2>
        <img :src="qrImage" alt="支付宝支付二维码">
        <p>{{ activeOrder?.order_no }}</p>
        <small>系统每 3 秒自动检查支付结果。</small>
      </div>
    </section>
  </main>
</template>
