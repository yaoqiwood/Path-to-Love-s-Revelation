import ViewCompat from '@/components/compat/ViewCompat.vue'
import TextCompat from '@/components/compat/TextCompat.vue'
import ImageCompat from '@/components/compat/ImageCompat.vue'
import ScrollViewCompat from '@/components/compat/ScrollViewCompat.vue'
import PickerCompat from '@/components/compat/PickerCompat.vue'
import SwitchCompat from '@/components/compat/SwitchCompat.vue'
import UniPaginationCompat from '@/components/compat/UniPaginationCompat.vue'
import BlockCompat from '@/components/compat/BlockCompat'

export default {
  install(app) {
    app.component('view', ViewCompat)
    app.component('text', TextCompat)
    app.component('image', ImageCompat)
    app.component('scroll-view', ScrollViewCompat)
    app.component('picker', PickerCompat)
    app.component('switch', SwitchCompat)
    app.component('uni-pagination', UniPaginationCompat)
    app.component('block', BlockCompat)
  }
}
