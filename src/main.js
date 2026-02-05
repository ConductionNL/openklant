import Vue from 'vue'
import App from './App.vue'

Vue.mixin({ methods: { t, n } })

const appElement = document.getElementById('openklant')
if (appElement) {
	new Vue({
		el: appElement,
		render: h => h(App),
	})
}
