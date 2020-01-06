import Vue from 'vue'
import Router from 'vue-router'
import Index from '@/components/page/Index'
import Photos from '@/components/page/Photos'
import Photo from '@/components/page/Photo'
import VideoPlayer from '@/components/page/VideoPlayer'
import Login from '@/components/page/Login'

import Books from '@/components/page/Books'
import Book from '@/components/page/Book'
Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Index',
      component: Index,
      meta: {
        requireAuth: true
      }
    },
    {
      path: '/photos',
      name: 'Photos',
      component: Photos,
      meta: {
        requireAuth: true
      }
    },
    {
      path: '/photo',
      name: 'Photo',
      component: Photo,
      meta: {
        requireAuth: true
      }
    },
    {
      path: '/video',
      name: 'Video',
      component: VideoPlayer,
      meta: {
        requireAuth: true
      }
    },
    {
      path: '/books',
      name: 'Books',
      component: Books,
      meta: {
        requireAuth: true
      }
    },
    {
      path: '/book',
      name: 'Book',
      component: Book,
      meta: {
        requireAuth: true
      }
    },
    {
      path: '/login',
      name: 'Login',
      component: Login,
      meta: {
        requireAuth: false
      }
    },
  ]
})
