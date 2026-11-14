import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '../stores/auth'
import HomeView from '../views/HomeView.vue'
import ProfileView from '../views/ProfileView.vue'
import HowToPlayView from '../views/HowToPlayView.vue'
import AuthView from '../views/AuthView.vue'
import RankingsView from '../views/RankingsView.vue'
import PlayView from '../views/PlayView.vue'
import GameView from '../views/GameView.vue'

// meta: { requiresAuth: true } means "you must be signed in to open this page"
export const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/profile', name: 'profile', component: ProfileView },
  { path: '/how-to-play', name: 'how-to-play', component: HowToPlayView },
  { path: '/rankings', name: 'rankings', component: RankingsView },
  {
    path: '/login',
    name: 'login',
    component: AuthView,
    meta: { bare: true }, // full screen page: App.vue hides the header
  },

  // Play pages: only for signed-in users
  { path: '/play', name: 'play', component: PlayView, meta: { requiresAuth: true } },
  { path: '/play/local', name: 'local-game', component: GameView, meta: { requiresAuth: true } },
  { path: '/play/computer', name: 'computer-game', component: GameView, meta: { requiresAuth: true } },
  { path: '/play/online', name: 'online-game', component: GameView, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Runs before every page change.
// If the page needs a sign-in and the user is not signed in, we send them to
// the login page. "redirect" remembers where they wanted to go, so after the
// sign-in they land there.
router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) return true

  const authStore = useAuthStore()

  // After a browser refresh we still have the token, but the user data is
  // gone: ask the server who this is before deciding.
  if (!authStore.isAuthenticated && authStore.token) {
    await authStore.fetchUser()
  }

  if (authStore.isAuthenticated) return true

  return { name: 'login', query: { redirect: to.fullPath } }
})

export default router