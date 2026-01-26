// ignition key
//➡️ mounts App.vue
// ➡️ loads router
// ➡️ loads Pinia (state store)
// ➡️ loads Tailwind CSS

import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
