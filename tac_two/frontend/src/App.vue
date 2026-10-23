
<script setup>
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

const tabs = [
  { label: 'Home', icon: 'home', path: '/', activeOn: '/' },
  { label: 'Play', icon: 'play', path: '/', activeOn: '/play' },
  { label: 'Learn', icon: 'learn', path: '/how-to-play', activeOn: '/how-to-play' },
  { label: 'Rankings', icon: 'trophy', path: '/', activeOn: '/rankings' },
]

function navigate(tab) {
  router.push(tab.path)
}
</script>

<template>
  <div class="app">
    <header class="header">
      <img class="logo" src="/design/tac2-logo.svg" alt="Tac2" />

      <nav class="tabs">
        <a
          v-for="tab in tabs"
          :key="tab.label"
          :href="tab.path"
           class="tab"
          :class="{ active: route.path === tab.activeOn }"
          @click.prevent="navigate(tab)"
        >
          <svg class="icon">
            <use :href="'#' + tab.icon"></use>
          </svg>
          {{ tab.label }}
        </a>
      </nav>

      <a
        href="/profile"
        class="profile"
        @click.prevent="router.push('/profile')"
      >
        <img
          class="profile-picture"
          src="/design/mochi-mascot.svg"
          alt=""
        />
        <span class="profile-text">
          <strong>Sofia</strong>
          <small>1,240 leaves</small>
        </span>
      </a>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>
