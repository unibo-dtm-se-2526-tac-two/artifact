<script setup>
// The tabs of the top bar (only Home works for now)
const tabs = [
  { label: 'Home', icon: 'home' },
  { label: 'Play', icon: 'play' },
  { label: 'Learn', icon: 'learn' },
  { label: 'Rankings', icon: 'trophy' },
]
import { ref } from 'vue'

const currentPage = ref('home')

function navigate(label) {
  if (label === 'Home') currentPage.value = 'home'
}

const profileStats = [
  { value: '58%', label: 'Win rate' },
  { value: '42', label: 'Games played' },
  { value: '8', label: 'Best streak' },
]

const achievements = [
  { icon: 'trophy', label: 'First win' },
  { icon: 'spark', label: '5 streak' },
  { icon: 'clock', label: 'Quick paws' },
]

const recentMatches = [
  { opponent: 'Mochi · Cozy', result: 'Won', date: 'Today' },
  { opponent: 'Martina', result: 'Lost', date: 'Yesterday' },
  { opponent: 'Mochi · Tricky', result: 'Won', date: 'Mar 18' },
]

const activeTab = 'Home'

// The three game mode cards
const modes = [
  { title: 'Pass & play', text: 'Share one cozy corner', icon: 'friends', colour: 'coral' },
  { title: 'Challenge Mochi', text: 'Easy, medium or tricky', icon: 'computer', colour: 'teal' },
  { title: 'Play online', text: 'Invite a friend by code', icon: 'online', colour: 'violet' },
]
</script>

<template>
  <div class="app">
    <!-- Top bar -->
    <header class="header">
      <img class="logo" src="/workspaces/artifact/docs/design/tac2-logo.svg" alt="Tac2" />

      <nav class="tabs">
        <a v-for="tab in tabs"
           :key="tab.label"
            href="#"
            class="tab"
            :class="{ active: tab.label === (currentPage === 'home' ? 'Home' : 'Profile') }"
            @click.prevent="navigate(tab.label)">
          <svg class="icon">
  <use :href="'#' + tab.icon"></use>
</svg>
          {{ tab.label }}
        </a>
      </nav>

      <a href="#" class="profile" @click.prevent="currentPage = 'profile'">
        <img class="profile-picture" src="/workspaces/artifact/docs/design/mochi-mascot.svg" alt="" />
        <span class="profile-text">
          <strong>Sofia</strong>
          <small>1,240 leaves</small>
        </span>
      </a>
    </header>

    <main>
      <template v-if="currentPage === 'home'">
      <!-- Big first section -->
      <section class="hero">
        <div class="hero-text">
          <p class="eyebrow">Think small. Win big.</p>
          <h1>Tic-tac-toe,<br />with a <span class="twist">twist.</span></h1>
          <p class="intro">
            Nine boards, one clever move at a time. Pick a square and decide where your rival
            plays next.
          </p>

          <div class="buttons">
            <a href="#modes" class="button">Choose a game →</a>
            <a href="#modes" class="link-button">
              <span class="play-circle">
                <svg class="icon"><use href="/workspaces/artifact/docs/design/tac2-interface-icons.svg#play" /></svg>
              </span>
              How to play
            </a>
          </div>

          <p class="players">Join 2,460 thoughtful players</p>
        </div>

        <div class="hero-picture">
          <div class="circle"></div>
          <div class="sun"></div>
          <div class="tile tile-x">×</div>
          <div class="tile tile-o">○</div>
          <div class="tip"><strong>Tip!</strong> Every move sends your rival somewhere new.</div>
          <img class="mochi" src="/workspaces/artifact/docs/design/mochi-mascot.svg" alt="Mochi the cat" />
        </div>
      </section>

      <!-- Game mode cards -->
      <section class="modes" id="modes">
        <div>
          <p class="eyebrow">Pick your pace</p>
          <h2>A game for every mood</h2>
        </div>

        <div class="cards">
          <a v-for="mode in modes" :key="mode.title" href="#" class="card" :class="mode.colour">
            <span class="card-icon">
              <svg class="icon"><use :href="'#' + mode.icon"></use></svg>
            </span>
            <span class="card-text">
              <strong>{{ mode.title }}</strong>
              <small>{{ mode.text }}</small>
            </span>
            <span>→</span>
          </a>
        </div>
      </section>
      </template>
<!-- Profile page -->
<section v-else-if="currentPage === 'profile'" class="profile-page">
  <div class="profile-banner">
    <div class="big-avatar">
      <img
        src="/workspaces/artifact/docs/design/mochi-mascot.svg"
        alt="Mochi the cat"
      />
    </div>

    <div class="profile-main">
      <p class="eyebrow">Player profile</p>
      <h1>Sofia Scardovi</h1>
      <p class="profile-meta">@sofiaplays · Joined this spring</p>
    </div>

    <button class="secondary-action">Edit profile</button>
  </div>

  <div class="stats-grid">
    <div
      v-for="stat in profileStats"
      :key="stat.label"
      class="stat-card"
    >
      <strong>{{ stat.value }}</strong>
      <span>{{ stat.label }}</span>
    </div>
  </div>

  <div class="dashboard-grid">
    <div class="dash-card progress-card">
      <div class="dash-title">
        <span>Your cozy progress</span>
        <strong>Level 7</strong>
      </div>

      <div class="level-row">
        <div class="level-badge">7</div>
        <div>
          <strong>Tactical Tabby</strong>
          <span>260 leaves to level 8</span>
          <div class="progress-track">
            <div class="progress-fill"></div>
          </div>
        </div>
      </div>

      <div class="achievement-row">
        <div v-for="item in achievements" :key="item.label">
          <svg class="icon">
            <use :href="'#' + item.icon" />
          </svg>
          <span>{{ item.label }}</span>
        </div>
      </div>
    </div>

    <div class="dash-card history-card">
      <div class="dash-title">
        <span>Recent matches</span>
        <strong>View all</strong>
      </div>

      <div
        v-for="match in recentMatches"
        :key="match.opponent"
        class="match-row"
      >
        <div class="match-symbol">×</div>

        <div>
          <strong>{{ match.opponent }}</strong>
          <span>{{ match.date }}</span>
        </div>

        <small :class="match.result.toLowerCase()">
          {{ match.result }}
        </small>
      </div>
    </div>
  </div>
</section>

    </main>
  </div>
</template>