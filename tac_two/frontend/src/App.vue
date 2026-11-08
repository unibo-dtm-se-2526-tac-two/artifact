
<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const ICONS = '/design/tac2-interface-icons.svg'
const EXTRA_ICONS = '/design/tac2-extra-icons.svg'

const menuOpen = ref(false)

// Detect when the user is inside an actual game
const isGamePage = computed(() =>
  ['/play/local', '/play/computer', '/play/online'].includes(route.path),
)

// Game title in the navbar
const gameModeTitle = computed(() => {
  if (route.path === '/play/local') return 'Pass & play'
  if (route.path === '/play/computer') return 'Challenge Mochi'
  if (route.path === '/play/online') return 'Online match'
  return ''
})

// Game subtitle in the navbar
const gameModeSubtitle = computed(() => {
  if (route.path === '/play/local') return 'Two players, one screen'
  if (route.path === '/play/online') return 'Playing together online'

  if (route.path === '/play/computer') {
    const labels = {
      easy: 'Kitten Steps',
      medium: 'Clever Paws',
      hard: 'Tiger Mode',
    }

    const level = String(route.query.level || 'medium').toLowerCase()
    return labels[level] || labels.medium
  }

  return ''
})

// Navigation tabs
const tabs = [
  { label: 'Home', icon: 'home', to: '/', activeOn: '/' },
  { label: 'Play', icon: 'play', to: '/play', activeOn: '/play' },
  { label: 'Learn', icon: 'learn', to: '/how-to-play', activeOn: '/how-to-play' },
  { label: 'Rankings', icon: 'trophy', to: '/rankings', activeOn: '/rankings' },
]

function isActive(tab) {
  return tab.activeOn === '/'
    ? route.path === '/'
    : route.path.startsWith(tab.activeOn)
}

function closeMenu() {
  menuOpen.value = false
}

onMounted(() => {
  authStore.fetchUser()
})
</script>

<template>
  <!-- Pages marked meta: { bare: true } in the router get the whole screen -->
  <RouterView v-if="route.meta.bare" />

  <div v-else class="app">
    <header class="header" :class="{ 'game-header': isGamePage }">
      <img class="logo" src="/design/tac2-logo.svg" alt="Tac2" />

      <!-- Normal navigation on non-game pages -->
      <nav v-if="!isGamePage" class="tabs">
        <RouterLink
          v-for="tab in tabs"
          :key="tab.label"
          :to="tab.to"
          class="tab"
          :class="{ active: isActive(tab) }"
        >
          <svg class="icon">
            <use :href="ICONS + '#' + tab.icon" />
          </svg>
          {{ tab.label }}
        </RouterLink>
      </nav>

      <!-- Game title -->
      <div v-if="isGamePage" class="game-mode-heading">
        <h1>{{ gameModeTitle }}</h1>
        <p>{{ gameModeSubtitle }}</p>
      </div>

      <!-- Right side: Sign in / Profile and burger menu -->
      <div v-if="isGamePage" class="game-header-right">

        <div class="header-right">
          <RouterLink
            v-if="!authStore.isAuthenticated"
            to="/login"
            class="signin"
          >
            <svg class="icon">
              <use :href="EXTRA_ICONS + '#login'" />
            </svg>
            Sign in
          </RouterLink>

          <RouterLink
            v-else
            to="/profile"
            class="profile"
          >
            <img
              class="profile-picture"
              src="/design/mochi-mascot.svg"
              alt=""
            />
            <span class="profile-text">
              <strong>{{ authStore.user?.username || 'Player' }}</strong>
              <small class="leaves">1,240 🍃</small>
            </span>
          </RouterLink>
        </div>

        <div class="game-menu">
          <button
            class="burger-button"
            :aria-expanded="menuOpen"
            aria-label="Toggle navigation menu"
            @click="menuOpen = !menuOpen"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>

          <nav v-if="menuOpen" class="burger-dropdown">
            <RouterLink
              v-for="tab in tabs"
              :key="tab.label"
              :to="tab.to"
              class="tab"
              :class="{ active: isActive(tab) }"
              @click="closeMenu"
            >
              <svg class="icon">
                <use :href="ICONS + '#' + tab.icon" />
              </svg>
              {{ tab.label }}
            </RouterLink>
          </nav>
        </div>
      </div>

      <!-- Sign in / Profile on normal pages -->
      <div v-if="!isGamePage" class="header-right">
        <RouterLink
          v-if="!authStore.isAuthenticated"
          to="/login"
          class="signin"
        >
          <svg class="icon">
            <use :href="EXTRA_ICONS + '#login'" />
          </svg>
          Sign in
        </RouterLink>

        <RouterLink
          v-else
          to="/profile"
          class="profile"
        >
          <img
            class="profile-picture"
            src="/design/mochi-mascot.svg"
            alt=""
          />
          <span class="profile-text">
            <strong>{{ authStore.user?.username || 'Player' }}</strong>
            <small class="leaves">1,240 🍃</small>
          </span>
        </RouterLink>
      </div>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
/* Main page container */
.app {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 28px 64px;
}

/* ----- Top bar ----- */
.header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 0;
  border-bottom: 1px solid var(--line);
}

.logo {
  height: 48px;
  flex-shrink: 0;
}

.tabs {
  display: flex;
  gap: 6px;
}

.tab {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  border-radius: var(--radius-sm);
  color: var(--muted);
  font-size: 17px;
  text-decoration: none;
}

.tab:hover {
  background: var(--line);
}

.tab.active {
  background: var(--teal-soft);
  color: var(--teal-dark);
}

/* ----- Header right ----- */
.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  min-width: max-content;
  white-space: nowrap;
  flex-shrink: 0;
}

.signin {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-wrap: nowrap;
  gap: 8px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  color: var(--teal);
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
}

.signin:hover {
  background: var(--teal-soft);
}

.profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px 8px 8px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--paper);
  box-shadow: var(--shadow);
  text-decoration: none;
}

.profile-picture {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  background: var(--gold-soft);
}

.profile-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.profile-text small {
  color: var(--muted);
}

.leaves {
  display: flex;
  align-items: center;
  gap: 4px;
}

.leaves svg {
  width: 14px;
  height: 14px;
  color: var(--teal);
}

/* ----- Game navbar ----- */
.game-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: center;
  gap: 12px;
}

.game-header .logo {
  justify-self: start;
}

/* Game title stays centered in the entire navbar */
.game-mode-heading {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: max-content;
  text-align: center;
  pointer-events: none;
}

.game-mode-heading h1 {
  margin: 0;
  font-family: var(--font-title);
  font-size: 23px;
  font-weight: 800;
  letter-spacing: -0.8px;
  line-height: 1.1;
  color: var(--ink);
}

.game-mode-heading p {
  margin: 3px 0 0;
  color: var(--muted);
  font-size: 13px;
}

/* Sign in and burger menu stay together on the right */
.game-header-right {
  grid-column: 3;
  justify-self: end;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

/* ----- Game burger menu ----- */
.game-menu {
  position: relative;
  display: flex;
  align-items: center;
}

.burger-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
  width: 42px;
  height: 42px;
  padding: 9px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: var(--paper);
  cursor: pointer;
  flex-shrink: 0;
}

.burger-button:hover {
  background: var(--line);
}

.burger-button span {
  display: block;
  width: 100%;
  height: 2px;
  border-radius: 2px;
  background: var(--ink);
}

.burger-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  z-index: 100;
  display: flex;
  flex-direction: column;
  min-width: 180px;
  padding: 8px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--paper);
  box-shadow: var(--shadow);
}

.burger-dropdown .tab {
  gap: 10px;
  padding: 12px;
  font-size: 15px;
}

.burger-dropdown .icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* ----- Smaller screens ----- */
@media (max-width: 700px) {
  .app {
    padding-left: 16px;
    padding-right: 16px;
  }

  .game-header {
    grid-template-columns: auto minmax(0, 1fr) auto;
    gap: 8px;
  }

  .game-header .logo {
    height: 38px;
  }

  .game-mode-heading h1 {
    font-size: 18px;
  }

  .game-mode-heading p {
    display: none;
  }

  .game-header-right {
    gap: 6px;
  }

  .signin {
    padding: 8px;
    font-size: 13px;
  }

  .profile {
    padding: 6px;
  }

  .profile-picture {
    width: 36px;
    height: 36px;
  }

  .profile-text {
    display: none;
  }

  .burger-button {
    width: 36px;
    height: 36px;
  }
}

/* Very narrow screens */
@media (max-width: 420px) {
  .app {
    padding-left: 12px;
    padding-right: 12px;
  }

  .game-header {
    gap: 5px;
  }

  .game-header .logo {
    height: 32px;
  }

  .game-mode-heading h1 {
    font-size: 16px;
  }

  .game-header-right {
    gap: 4px;
  }

  .signin {
    gap: 4px;
    padding: 6px;
    font-size: 12px;
  }

  .burger-button {
    width: 32px;
    height: 32px;
  }
}
</style>
