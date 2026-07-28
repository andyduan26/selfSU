import { defineStore } from 'pinia'
import http from '../api/http'

const savedAccessToken = sessionStorage.getItem('accessToken') || ''
const savedRefreshToken = sessionStorage.getItem('refreshToken') || ''
const savedUser = sessionStorage.getItem('currentUser')

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: savedAccessToken,
    refreshToken: savedRefreshToken,
    user: savedUser ? JSON.parse(savedUser) : null,
    teacherStatus: null,
    loading: false,
    error: '',
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken),
  },
  actions: {
    setSession(payload) {
      this.accessToken = payload.access
      this.refreshToken = payload.refresh
      this.user = payload.user
      sessionStorage.setItem('accessToken', payload.access)
      sessionStorage.setItem('refreshToken', payload.refresh)
      sessionStorage.setItem('currentUser', JSON.stringify(payload.user))
    },
    clearSession() {
      this.accessToken = ''
      this.refreshToken = ''
      this.user = null
      this.teacherStatus = null
      sessionStorage.removeItem('accessToken')
      sessionStorage.removeItem('refreshToken')
      sessionStorage.removeItem('currentUser')
    },
    async register(form) {
      this.loading = true
      this.error = ''
      try {
        const response = await http.post('/auth/register/', form)
        this.setSession(response.data.data)
      } catch (error) {
        this.error = '注册失败，请检查账号、邮箱或手机号是否已存在'
        throw error
      } finally {
        this.loading = false
      }
    },
    async login(form) {
      this.loading = true
      this.error = ''
      try {
        const response = await http.post('/auth/login/', form)
        this.setSession(response.data.data)
      } catch (error) {
        this.error = '账号或密码错误'
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchMe() {
      const response = await http.get('/auth/me/')
      this.user = response.data.data
      sessionStorage.setItem('currentUser', JSON.stringify(this.user))
    },
    async fetchTeacherStatus() {
      const response = await http.get('/teacher/status/')
      this.teacherStatus = response.data.data
      return this.teacherStatus
    },
    async submitTeacherApplication(form) {
      this.loading = true
      this.error = ''
      try {
        const response = await http.post('/teacher/applications/', form)
        await this.fetchTeacherStatus()
        return response.data.data
      } catch (error) {
        this.error = '教师认证申请提交失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchTeacherCourses() {
      const response = await http.get('/teacher/courses/')
      return response.data.data
    },
    async fetchMyOrders() {
      const response = await http.get('/orders/')
      return response.data.data
    },
    async fetchMyFavorites() {
      const response = await http.get('/favorites/')
      return response.data.data
    },
    async fetchTeacherOrders() {
      const response = await http.get('/teacher/orders/')
      return response.data.data
    },
    async fetchTeacherIncomeSummary() {
      const response = await http.get('/teacher/income/summary/')
      return response.data.data
    },
    async fetchTeacherWithdraws() {
      const response = await http.get('/teacher/withdraws/')
      return response.data.data
    },
    async createTeacherWithdraw(payload) {
      const response = await http.post('/teacher/withdraws/', payload)
      return response.data.data
    },
    async createTeacherCourse(payload) {
      const response = await http.post('/teacher/courses/', payload)
      return response.data.data
    },
    async updateTeacherCourse(id, payload) {
      const response = await http.put(`/teacher/courses/${id}/`, payload)
      return response.data.data
    },
    async deleteTeacherCourse(id) {
      await http.delete(`/teacher/courses/${id}/`)
    },
    async createR2Upload(file, folder) {
      const response = await http.post('/uploads/r2/presign/', {
        filename: file.name,
        content_type: file.type || 'application/octet-stream',
        folder,
      })
      const uploadResponse = await fetch(response.data.data.upload_url, {
        method: 'PUT',
        headers: {
          'Content-Type': file.type || 'application/octet-stream',
        },
        body: file,
      })
      if (!uploadResponse.ok) {
        throw new Error('R2 文件上传失败')
      }
      return response.data.data.public_url
    },
    async updateProfile(form) {
      this.loading = true
      this.error = ''
      try {
        const response = await http.put('/auth/me/', form)
        this.user = response.data.data
        sessionStorage.setItem('currentUser', JSON.stringify(this.user))
      } catch (error) {
        this.error = '资料保存失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    logout() {
      this.clearSession()
    },
  },
})
