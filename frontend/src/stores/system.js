import { defineStore } from 'pinia'
import http from '../api/http'

export const useSystemStore = defineStore('system', {
  state: () => ({
    health: null,
    loading: false,
    error: '',
  }),
  actions: {
    async fetchHealth() {
      this.loading = true
      this.error = ''

      try {
        const response = await http.get('/health/')
        this.health = response.data.data
      } catch (error) {
        this.error = '后端服务暂时无法连接'
      } finally {
        this.loading = false
      }
    },
  },
})
