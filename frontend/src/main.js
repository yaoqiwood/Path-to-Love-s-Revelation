import './platform/install-globals'
import './styles/base.less'

import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import { registerAppRouter } from './router/holder'
import compatComponentsPlugin from './plugins/compat-components'
import legacyPageLifecyclePlugin from './plugins/legacy-page-lifecycle'
import { ensureMockBootstrap } from './platform/mock-presets'

registerAppRouter(router)
ensureMockBootstrap()

const app = createApp(App)

app.use(router)
app.use(compatComponentsPlugin)
app.use(legacyPageLifecyclePlugin)

app.mount('#app')
