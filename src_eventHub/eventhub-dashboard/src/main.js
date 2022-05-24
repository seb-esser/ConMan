import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import VNetworkGraph from "v-network-graph"
import "v-network-graph/style.css"

loadFonts()

createApp(App)
  .use(router)
  .use(vuetify)
    .use(VNetworkGraph)
  .mount('#app')
