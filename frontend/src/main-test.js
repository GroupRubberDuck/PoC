console.log("🚀 L'Isola Vue sta cercando di avviarsi!");
import { createApp } from 'vue'
import TestIntegration from './TestIntegration.vue'

// Si aggancerà a un div con id="vue-test"
createApp(TestIntegration).mount('#vue-test')