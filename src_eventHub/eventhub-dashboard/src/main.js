import App from './App.vue'
import { createApp } from 'vue'
import router from './router'

// import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'

// Import Bootstrap and BootstrapVue CSS files (order is important)
import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
// import BootstrapVue from "bootstrap-vue";


createApp(App).use(router).mount('#app')
// App.use(BootstrapVue)


