
import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import ProfileView from '../views/ProfileView.vue'
import HowToPlayView from '../views/HowToPlayView.vue'
import AuthView from '../views/AuthView.vue'
import RankingsView from '../views/RankingsView.vue'
import PlayView from '../views/PlayView.vue'
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

{
  path: '/login',
  name: 'login',
  component: AuthView,
},
{
  path: '/rankings',
  name: 'rankings',
  component: RankingsView,
},
{
  path: '/play',
  name: 'play',
  component: PlayView,
},
{
    path: '/login',
    name: 'login',
    component: AuthView,
    meta: { bare: true }, // full screen page: App.vue hides the header
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
