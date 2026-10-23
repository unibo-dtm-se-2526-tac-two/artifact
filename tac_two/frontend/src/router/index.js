
import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import ProfileView from '../views/ProfileView.vue'
import HowToPlayView from '../views/HowToPlayView.vue'

export const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
  },
  {
    path: '/how-to-play',
    name: 'how-to-play',
    component: HowToPlayView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
