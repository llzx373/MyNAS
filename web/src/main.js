// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import 'vue2-animate/dist/vue2-animate.min.css'
import App from './App.vue';
Vue.use(ElementUI);
import router from './router'
import VueCookies from 'vue-cookies'
import Prism from 'prismjs';
import axios from "axios";
Vue.use(Prism)
Vue.use(VueCookies)
Vue.use(axios)
Vue.config.productionTip = false

router.beforeEach((to, from, next) => {
  if (to.meta.requireAuth) {
    if ($cookies.get('token') && $cookies.get('username')) {
      next();
    } else {
      next({
        path: '/login',
      })
    }
  }
  else {
    next();
  }
})
axios.interceptors.response.use(function (response) {
  if (response.config.url.endsWith('/api/login')){
    return response
  }
  if ($cookies.get('token') && $cookies.get('username')) {
    
    return response
  } else {
    router.replace({
      path: '/login',
    })
  }
})

Vue.prototype.$addStorageEvent = function (type,key, data) {
  if (type === 1) {
    // 创建一个StorageEvent事件
    var newStorageEvent = document.createEvent('StorageEvent');
    const storage = {
      setItem: function (k, val) {
        localStorage.setItem(k, val);
        // 初始化创建的事件
        newStorageEvent.initStorageEvent('setItem', false, false, k, null, val, null, null);
        // 派发对象
        window.dispatchEvent(newStorageEvent);
      }
    }
    return storage.setItem(key, data);
  } else {
    // 创建一个StorageEvent事件
    var newStorageEvent = document.createEvent('StorageEvent');
    const storage = {
      setItem: function (k, val) {
        sessionStorage.setItem(k, val);
        // 初始化创建的事件
        newStorageEvent.initStorageEvent('setItem', false, false, k, null, val, null, null);
        // 派发对象
        window.dispatchEvent(newStorageEvent);
      }
    }
    return storage.setItem(key, data);
  }
}

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>',
  render: h => h(App)
})
