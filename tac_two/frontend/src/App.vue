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
  if (label === 'Play') currentPage.value = 'home'
  if (label === 'Learn') currentPage.value = 'how-to-play'
  if (label === 'Rankings') currentPage.value = 'home'

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
      <img class="logo" src="/design/tac2-logo.svg" alt="Tac2" />

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
        <img class="profile-picture" src="/design/mochi-mascot.svg" alt="" />
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
            <a href="#modes" class="link-button" @click.prevent="currentPage = 'how-to-play'">
              <span class="play-circle">
                <svg class="icon"><use href="/design/tac2-interface-icons.svg#play" /></svg>
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
          <img class="mochi" src="/design/mochi-mascot.svg" alt="Mochi the cat" />
        </div>
      </section>

      </template>
<!-- Profile page -->
<section v-else-if="currentPage === 'profile'" class="profile-page">
  <div class="profile-banner">
    <div class="big-avatar">
      <img
        src="/design/mochi-mascot.svg"
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

<!-- How to Play page -->
<section
  v-else-if="currentPage === 'how-to-play'"
  class="how-to-play-page"
>
  <button
    class="back-link"
    @click="currentPage = 'home'"
  >
    ← Back to Home
  </button>

  <section class="rules-hero">
    <p class="eyebrow">The little guide</p>
    <h1>Think small.<br />Play <span>clever.</span></h1>
    <p class="rules-intro">
      Nine little boards. One big strategy.
      Learn the twist that makes TAC2 different.
    </p>
    <div class="rule-badges">
      <span>✦ Easy to learn</span>
      <span>♟ Two players</span>
      <span>♡ Strategy first</span>
    </div>
  </section>

  <section class="rules-section">
    <div class="section-heading">
      <p class="eyebrow">The basics</p>
      <h2>Three steps to get started</h2>
    </div>

    <div class="rule-cards">
      <article class="rule-card coral">
        <div class="rule-number">01</div>
        <div class="mini-board">
          <span>×</span><span></span><span>○</span>
          <span></span><span>×</span><span></span>
          <span>○</span><span></span><span></span>
        </div>
        <h3>Take your turn</h3>
        <p>
          Players take turns placing their mark, X or O,
          in an empty square.
        </p>
      </article>

      <article class="rule-card teal">
        <div class="rule-number">02</div>
        <div class="mini-board">
          <span></span><span>×</span><span></span>
          <span></span><span>○</span><span></span>
          <span></span><span>×</span><span></span>
        </div>
        <h3>Think one move ahead</h3>
        <p>
          Your move determines which small board your
          opponent must play in next.
        </p>
      </article>

      <article class="rule-card violet">
        <div class="rule-number">03</div>
        <div class="mini-board winning-board">
          <span>×</span><span>×</span><span>×</span>
          <span>○</span><span>○</span><span></span>
          <span></span><span></span><span></span>
        </div>
        <h3>Win the big board</h3>
        <p>
          Win small boards by making three in a row.
          Win the overall game by claiming three small
          boards in a row.
        </p>
      </article>
    </div>
  </section>

  <section class="twist-section">
    <div class="twist-copy">
      <p class="eyebrow">The special twist</p>
      <h2>Your square decides their board.</h2>
      <p>
        Every square on a small board corresponds to
        another board in the larger 3 × 3 grid.
        If you play in the top-right square, your
        opponent goes to the top-right board.
      </p>
      <p>
        So don't just ask, “Where can I win?”
        Ask, “Where will my move send them?”
      </p>
    </div>

    <div class="twist-example">
      <div class="example-label">A move changes everything</div>
      <div class="big-board">
        <div class="small-board">
          <span></span><span></span><span></span>
          <span></span><span>×</span><span></span>
          <span></span><span></span><span></span>
        </div>
        <div class="small-board"><span></span><span></span><span></span><span></span><span>○</span><span></span><span></span><span></span><span></span></div>
        <div class="small-board"><span></span><span>×</span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
        <div class="small-board"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
        <div class="small-board"><span></span><span></span><span></span><span></span><span>○</span><span></span><span></span><span></span><span></span></div>
        <div class="small-board target-board"><span></span><span></span><span></span><span></span><span>×</span><span></span><span></span><span></span><span></span></div>
        <div class="small-board"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
        <div class="small-board"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
        <div class="small-board"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
      </div>
      <p class="example-caption">
        Play in a square, send your rival to the
        matching board.
      </p>
    </div>
  </section>

  <section class="tips-section">
    <p class="eyebrow">A few friendly reminders</p>
    <h2>Play smart, stay cozy.</h2>

    <div class="tip-list">
      <div class="tip-item">
        <span class="tip-icon">✦</span>
        <div>
          <h3>Plan ahead</h3>
          <p>Think about your next move and your opponent's options.</p>
        </div>
      </div>

      <div class="tip-item">
        <span class="tip-icon">♡</span>
        <div>
          <h3>Watch the whole board</h3>
          <p>A small-board win can bring you closer to the big one.</p>
        </div>
      </div>

      <div class="tip-item">
        <span class="tip-icon">☁</span>
        <div>
          <h3>Enjoy the game</h3>
          <p>Every round is a chance to learn a new strategy.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="rules-cta">
    <div>
      <p class="eyebrow">Ready when you are</p>
      <h2>Let's make a move.</h2>
      <p>Put your new strategy to the test.</p>
    </div>
    <button
      class="button"
      @click="currentPage = 'home'"
    >
      Choose a game →
    </button>
  </section>
</section>
    </main>
  </div>
</template>