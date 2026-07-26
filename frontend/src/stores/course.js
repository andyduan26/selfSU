import { defineStore } from 'pinia'
import http from '../api/http'

export const useCourseStore = defineStore('course', {
  state: () => ({
    courses: [],
    currentCourse: null,
    currentTeacher: null,
    currentLesson: null,
    loading: false,
    error: '',
  }),
  getters: {
    categories: (state) => [...new Set(state.courses.map((course) => course.category).filter(Boolean))],
  },
  actions: {
    async fetchCourses(category = '') {
      this.loading = true
      this.error = ''
      try {
        const response = await http.get('/courses/', { params: category ? { category } : {} })
        this.courses = response.data.data
        return this.courses
      } catch (error) {
        this.error = '课程加载失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchCourse(id) {
      const response = await http.get(`/courses/${id}/`)
      this.currentCourse = response.data.data
      return this.currentCourse
    },
    async fetchTeacher(id) {
      const response = await http.get(`/teachers/${id}/`)
      this.currentTeacher = response.data.data
      return this.currentTeacher
    },
    async fetchLessonPlay(id) {
      const response = await http.get(`/lessons/${id}/play/`)
      this.currentLesson = response.data.data
      return this.currentLesson
    },
    async createCourseOrder(courseId, paymentMethod = 'alipay') {
      const response = await http.post(`/courses/${courseId}/orders/`, {
        payment_method: paymentMethod,
      })
      return response.data.data
    },
  },
})
