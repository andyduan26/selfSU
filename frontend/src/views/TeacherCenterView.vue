<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { storeToRefs } from 'pinia'

import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const { teacherStatus } = storeToRefs(authStore)
const isTeacher = computed(() => teacherStatus.value?.is_teacher)
const applicationStatus = computed(() => teacherStatus.value?.application_status)
const courses = ref([])
const teacherOrders = ref([])
const incomeSummary = ref(null)
const withdraws = ref([])
const editingId = ref(null)
const courseForm = reactive(createEmptyCourse())
const withdrawForm = reactive({
  amount: '',
  account_name: '',
  account_no: '',
})
const uploadMessage = ref('')
const withdrawMessage = ref('')
const withdrawError = ref('')

function createEmptyCourse() {
  return {
    title: '',
    cover: '',
    category: '',
    price: '0.00',
    summary: '',
    suitable_audience: '',
    chapters: [
      {
        title: '',
        summary: '',
        sort_order: 1,
        lessons: [
          { title: '', video_file: '', is_trial: false, sort_order: 1 },
        ],
      },
    ],
  }
}

function resetForm() {
  Object.assign(courseForm, createEmptyCourse())
  editingId.value = null
}

async function loadCourses() {
  if (isTeacher.value) {
    courses.value = await authStore.fetchTeacherCourses()
    teacherOrders.value = await authStore.fetchTeacherOrders()
    incomeSummary.value = await authStore.fetchTeacherIncomeSummary()
    withdraws.value = await authStore.fetchTeacherWithdraws()
  }
}

onMounted(() => {
  authStore.fetchTeacherStatus().then(loadCourses)
})

function addChapter() {
  courseForm.chapters.push({
    title: '',
    summary: '',
    sort_order: courseForm.chapters.length + 1,
    lessons: [{ title: '', video_file: '', is_trial: false, sort_order: 1 }],
  })
}

function addLesson(chapter) {
  chapter.lessons.push({ title: '', video_file: '', is_trial: false, sort_order: chapter.lessons.length + 1 })
}

function removeChapter(index) {
  courseForm.chapters.splice(index, 1)
}

function removeLesson(chapter, index) {
  chapter.lessons.splice(index, 1)
}

function editCourse(course) {
  editingId.value = course.id
  Object.assign(courseForm, {
    title: course.title,
    cover: course.cover || '',
    category: course.category,
    price: course.price,
    summary: course.summary,
    suitable_audience: course.suitable_audience,
    chapters: course.chapters.map((chapter) => ({
      title: chapter.title,
      summary: chapter.summary,
      sort_order: chapter.sort_order,
      lessons: chapter.lessons.map((lesson) => ({
        title: lesson.title,
        video_file: lesson.video_file || '',
        is_trial: lesson.is_trial,
        sort_order: lesson.sort_order,
      })),
    })),
  })
}

async function submitCourse() {
  if (editingId.value) {
    await authStore.updateTeacherCourse(editingId.value, courseForm)
  } else {
    await authStore.createTeacherCourse(courseForm)
  }
  resetForm()
  await loadCourses()
}

async function uploadCover(event) {
  const file = event.target.files?.[0]
  if (!file) return
  uploadMessage.value = '封面上传中'
  courseForm.cover = await authStore.createR2Upload(file, 'course-covers')
  uploadMessage.value = '封面已上传'
}

async function uploadLessonVideo(event, lesson) {
  const file = event.target.files?.[0]
  if (!file) return
  uploadMessage.value = '视频上传中，请保持页面打开'
  lesson.video_file = await authStore.createR2Upload(file, 'course-videos')
  uploadMessage.value = '视频已上传'
}

async function deleteCourse(course) {
  await authStore.deleteTeacherCourse(course.id)
  await loadCourses()
}

async function submitWithdraw() {
  withdrawMessage.value = ''
  withdrawError.value = ''
  try {
    await authStore.createTeacherWithdraw(withdrawForm)
    withdrawMessage.value = '提现申请已提交，请等待管理员审核。'
    Object.assign(withdrawForm, {
      amount: '',
      account_name: '',
      account_no: '',
    })
    await loadCourses()
  } catch (error) {
    withdrawError.value = error.response?.data?.message || '提现申请提交失败'
  }
}
</script>

<template>
  <main class="profile-page">
    <section class="profile-header">
      <p class="eyebrow">教师中心</p>
      <h1>{{ isTeacher ? '课程创作中心' : '抱歉，请先申请认证教师。' }}</h1>
    </section>

    <section v-if="isTeacher" class="teacher-workspace">
      <section class="income-panel">
        <div>
          <span>总收益</span>
          <strong>¥ {{ incomeSummary?.total_income || '0.00' }}</strong>
        </div>
        <div>
          <span>可提现</span>
          <strong>¥ {{ incomeSummary?.available_amount || '0.00' }}</strong>
        </div>
        <div>
          <span>已提现</span>
          <strong>¥ {{ incomeSummary?.withdrawn_amount || '0.00' }}</strong>
        </div>
      </section>

      <form class="course-editor withdraw-editor" @submit.prevent="submitWithdraw">
        <h2>申请提现</h2>
        <label>
          <span>提现金额</span>
          <input v-model="withdrawForm.amount" type="number" min="0.01" step="0.01" required>
        </label>
        <label>
          <span>收款人</span>
          <input v-model="withdrawForm.account_name" required>
        </label>
        <label>
          <span>收款账号</span>
          <input v-model="withdrawForm.account_no" required>
        </label>
        <button type="submit">提交提现申请</button>
        <p v-if="withdrawMessage" class="notice">{{ withdrawMessage }}</p>
        <p v-if="withdrawError" class="form-error">{{ withdrawError }}</p>
      </form>

      <form class="course-editor" @submit.prevent="submitCourse">
        <h2>{{ editingId ? '编辑课程作品' : '新增课程作品' }}</h2>
        <label>
          <span>标题</span>
          <input v-model="courseForm.title" required>
        </label>
        <label>
          <span>封面地址</span>
          <input v-model="courseForm.cover" placeholder="后续接 Cloudflare R2 封面地址">
        </label>
        <label>
          <span>上传封面到 R2</span>
          <input type="file" accept="image/*" @change="uploadCover">
        </label>
        <p v-if="uploadMessage" class="notice">{{ uploadMessage }}</p>
        <label>
          <span>分类</span>
          <input v-model="courseForm.category" required>
        </label>
        <label>
          <span>价格</span>
          <input v-model="courseForm.price" type="number" min="0" step="0.01" required>
        </label>
        <label>
          <span>简介</span>
          <textarea v-model="courseForm.summary" rows="4" required />
        </label>
        <label>
          <span>适合人群</span>
          <textarea v-model="courseForm.suitable_audience" rows="3" required />
        </label>

        <section v-for="(chapter, chapterIndex) in courseForm.chapters" :key="chapterIndex" class="chapter-editor">
          <div class="editor-row">
            <strong>章节 {{ chapterIndex + 1 }}</strong>
            <button type="button" class="inline-button" @click="removeChapter(chapterIndex)">删除章节</button>
          </div>
          <label>
            <span>章节标题</span>
            <input v-model="chapter.title" required>
          </label>
          <label>
            <span>章节简介</span>
            <textarea v-model="chapter.summary" rows="2" />
          </label>
          <label>
            <span>排序</span>
            <input v-model.number="chapter.sort_order" type="number" min="0">
          </label>

          <section v-for="(lesson, lessonIndex) in chapter.lessons" :key="lessonIndex" class="lesson-editor">
            <div class="editor-row">
              <span>小节 {{ lessonIndex + 1 }}</span>
              <button type="button" class="inline-button" @click="removeLesson(chapter, lessonIndex)">删除小节</button>
            </div>
            <label>
              <span>小节标题</span>
              <input v-model="lesson.title" required>
            </label>
            <label>
              <span>视频文件 URL</span>
              <input v-model="lesson.video_file" placeholder="上传后自动填入 R2 URL">
            </label>
            <label>
              <span>上传视频到 R2</span>
              <input type="file" accept="video/*" @change="uploadLessonVideo($event, lesson)">
            </label>
            <label class="check-field">
              <input v-model="lesson.is_trial" type="checkbox">
              <span>允许试看</span>
            </label>
            <label>
              <span>排序</span>
              <input v-model.number="lesson.sort_order" type="number" min="0">
            </label>
          </section>

          <button type="button" class="secondary-button" @click="addLesson(chapter)">新增小节</button>
        </section>

        <button type="button" class="secondary-button" @click="addChapter">新增章节</button>
        <button type="submit">{{ editingId ? '保存修改并提交审核' : '上传课程并提交审核' }}</button>
      </form>

      <section class="course-list">
        <h2>我的作品</h2>
        <article v-for="course in courses" :key="course.id" class="course-item">
          <div>
            <strong>{{ course.title }}</strong>
            <span>{{ course.category }} / {{ course.price }} / {{ course.audit_status }}</span>
            <small v-if="course.audit_reject_reason">拒绝原因：{{ course.audit_reject_reason }}</small>
          </div>
          <div class="course-actions">
            <button type="button" class="inline-button" @click="editCourse(course)">编辑</button>
            <button type="button" class="inline-button" @click="deleteCourse(course)">删除</button>
          </div>
        </article>
      </section>

      <section class="course-list teacher-orders">
        <h2>课程订单</h2>
        <article v-for="order in teacherOrders" :key="order.id" class="course-item">
          <div>
            <strong>{{ order.course_title }}</strong>
            <span>{{ order.order_no }} / {{ order.amount }} / {{ order.pay_status }} / {{ order.payment_method }}</span>
          </div>
        </article>
      </section>

      <section class="course-list teacher-orders">
        <h2>提现记录</h2>
        <article v-for="withdraw in withdraws" :key="withdraw.id" class="course-item">
          <div>
            <strong>¥ {{ withdraw.amount }}</strong>
            <span>{{ withdraw.account_name }} / {{ withdraw.account_no }} / {{ withdraw.status }}</span>
            <small v-if="withdraw.review_note">审核备注：{{ withdraw.review_note }}</small>
          </div>
        </article>
      </section>
    </section>

    <section v-else class="teacher-panel">
      <p v-if="applicationStatus === 'pending'">当前认证状态：待审核。耐心等待2-3个工作日，结果会邮箱通知。</p>
      <p v-else-if="applicationStatus === 'rejected'">当前认证状态：未通过。请修改资料后重新申请。</p>
      <p v-else>成为认证教师后，才能进入教师中心。</p>
      <RouterLink class="text-link" to="/teacher/apply">申请认证教师</RouterLink>
    </section>
  </main>
</template>
