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
