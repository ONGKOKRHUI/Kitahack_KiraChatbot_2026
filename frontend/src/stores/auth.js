import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null
  }),
  actions: {
    async login(username, password) {
      try {
        // CALL THE REAL BACKEND
        const res = await axios.post('http://localhost:8000/api/v1/auth/token', {
          username: username,
          password: password
        });
        
        this.token = res.data.access_token;
        this.user = username;
        
        // Save to LocalStorage so refresh doesn't logout
        localStorage.setItem('token', this.token);
        
        // Configure Axios to use this token for future requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
        
        return true;
      } catch (error) {
        console.error("Login Failed", error);
        return false;
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    }
  }
})