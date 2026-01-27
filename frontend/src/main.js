// ignition key
//➡️ mounts App.vue
// ➡️ loads router
// ➡️ loads Pinia (state store)
// ➡️ loads Tailwind CSS

import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth' // import auth store
import axios from 'axios' // import axios to set default headers
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Check auth and redirect if needed BEFORE mounting
const authStore = useAuthStore()
if (!authStore.token) {
  router.push('/login')  // Force redirect to login if no token
}

// Set axios default Authorization header if token exists in localStorage
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

app.mount('#app')
