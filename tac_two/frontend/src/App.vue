<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const ICONS = '/design/tac2-interface-icons.svg'
const EXTRA_ICONS = '/design/tac2-extra-icons.svg' // the extra icon file (login, mail, ...)

// "to" = where the tab goes, "activeOn" = which page makes the tab look selected
const tabs = [
  { label: 'Home', icon: 'home', to: '/', activeOn: '/' },
  { label: 'Play', icon: 'play', to: '/play', activeOn: '/play' },
  { label: 'Learn', icon: 'learn', to: '/how-to-play', activeOn: '/how-to-play' },
  { label: 'Rankings', icon: 'trophy', to: '/rankings', activeOn: '/rankings' },
  // Add this tab when you have the /settings route:
  // { label: 'Settings', icon: 'settings', to: '/settings', activeOn: '/settings' },
]

// Home is only active on "/", the other tabs are also active on sub-pages (/play/local)
function isActive(tab) {
  return tab.activeOn === '/' ? route.path === '/' : route.path.startsWith(tab.activeOn)
}
</script>

<template>
  <!-- Pages marked meta: { bare: true } in the router (the sign-in page) get the whole screen -->
  <RouterView v-if="route.meta.bare" />

  <div v-else class="app">
    <header class="header">
      <img class="logo" src="/design/tac2-logo.svg" alt="Tac2" />

      <nav class="tabs">
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

      <div class="header-right">
        <RouterLink to="/login" class="signin">
          <svg class="icon">
            <use :href="EXTRA_ICONS + '#login'" />
          </svg>
          Sign in
        </RouterLink>

        <RouterLink to="/profile" class="profile">
          <img class="profile-picture" src="/design/mochi-mascot.svg" alt="" />
          <span class="profile-text">
            <strong>Sofia</strong>
            <small class="leaves">1,240 🍃 </small>
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
/* Keeps the page in the middle on big screens */
.app {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 28px 64px;
}

/* ----- Top bar ----- */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 0;
  border-bottom: 1px solid var(--line);
}

.logo {
  height: 48px;
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
}

.tab:hover {
  background: var(--line);
}

.tab.active {
  background: var(--teal-soft);
  color: var(--teal-dark);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.signin {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  color: var(--teal);
  font-size: 14px;
  font-weight: 700;
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

/* number + leaf icon */
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

/* ----- Small screens ----- */
@media (max-width: 880px) {
  .header {
    flex-wrap: wrap;
    gap: 12px;
  }

  .tabs {
    order: 3;
    width: 100%;
    justify-content: center;
  }

  .tab {
    gap: 6px;
    padding: 10px 12px;
    font-size: 15px;
  }
}
</style>