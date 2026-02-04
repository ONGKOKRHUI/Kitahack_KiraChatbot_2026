# Frontend Fix Instructions

### 1. Fix the Layout Issue (Left Side Only)

The file `frontend/src/assets/main.css` contains default styles that restrict the width and force a grid layout on larger screens. You need to remove these to allow the app to take up the full screen.

**File:** `frontend/src/assets/main.css`

**Action:** Replace the entire content of the file with the following:

```css
@import './base.css';

@tailwind base;
@tailwind components;
@tailwind utilities;

/* Ensure full height for the application */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}
```

This removes the `max-width`, `padding`, and the `display: grid` rules that were constraining the layout.

### 2. Fix the Authentication Redirection (401 Error)

The issue is that when your token is invalid or expired, the backend returns a `401 Unauthorized` error, but the frontend doesn't know what to do with it, so it stays on the page. We need to tell the frontend to listen for these errors and redirect you to the login page automatically.

**File:** `frontend/src/main.js`

**Action:** Update the file to include an Axios interceptor.

1.  **Remove** the manual check that looks like this:
    ```javascript
    // Check auth and redirect if needed BEFORE mounting
    const authStore = useAuthStore()
    if (!authStore.token) {
      router.push('/login')  // Force redirect to login if no token
    }
    ```

2.  **Add** this code block in its place (or after `app.use(router)`):

    ```javascript
    const authStore = useAuthStore()

    // Add a response interceptor to handle 401 errors globally
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response && error.response.status === 401) {
          // If the backend says "Unauthorized", clear the token and redirect to login
          authStore.logout()
          router.push('/login')
        }
        return Promise.reject(error)
      }
    )
    ```

**Full `frontend/src/main.js` for reference:**

```javascript
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth'
import axios from 'axios'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

const authStore = useAuthStore()

// Global error handler for 401 Unauthorized
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      authStore.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

// Set axios default Authorization header if token exists
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

app.mount('#app')
```
