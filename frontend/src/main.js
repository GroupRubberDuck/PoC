import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router.js' // Importiamo il router che abbiamo appena creato

const app = createApp(App)

app.use(router) // Diciamo a Vue di usare il router
app.mount('#app')