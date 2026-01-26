// Manages login state
// It simulates a login by accepting any non-empty username and password.
// is ready to be replaced with real API calls in production. and connect to backend later.

import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null
  }),
  actions: {
    async login(username, password) {
      // In production: const res = await axios.post('http://localhost:8000/api/v1/login', {username, password})
      // For Demo: We just check if fields are not empty
      if (username && password) {
        this.token = "fake-jwt-token-123"; 
        this.user = username;
        localStorage.setItem('token', this.token);
        return true;
      }
      return false;
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
    }
  }
})