import {createApp} from 'vue'
import {createPinia} from 'pinia'
import {setupZod} from './lib/zod'
import router from './router'
import App from './App.vue'
import './assets/index.css'

setupZod()
const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#root')
