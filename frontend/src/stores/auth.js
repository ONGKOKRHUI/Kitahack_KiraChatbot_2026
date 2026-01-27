// attempts to manage authentication state (login/logout) using Pinia store
// calls backend API to authenticate and store JWT token

import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null
  }),
  actions: {
    async login(username, password) {
      try {
        const res = await axios.post('http://localhost:8000/api/v1/auth/token', { username, password })
        this.token = res.data.access_token
        this.user = res.data.user
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        return true
      } catch (error) {
        return false
      }
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete axios.defaults.headers.common['Authorization']
    },
    // Add: Check if token is valid (optional, for expiry handling)
    isTokenValid() {
      if (!this.token) return false
      try {
        const payload = jwt.decode(this.token, null, { complete: true })  // Decode without verification for client-side check
        return payload.exp > Date.now() / 1000
      } catch {
        return false
      }
    }
  }
  })