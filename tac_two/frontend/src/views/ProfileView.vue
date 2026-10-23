
<script setup>
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
</script>

<template>
  <section class="profile-page">
    <div class="profile-banner">
      <div class="big-avatar">
        <img src="/design/mochi-mascot.svg" alt="Mochi the cat" />
      </div>

      <div class="profile-main">
        <p class="eyebrow">Player profile</p>
        <h1>Sofia Scardovi</h1>
        <p class="profile-meta">@sofiaplays · Joined this spring</p>
      </div>

      <button class="secondary-action">Edit profile</button>
    </div>

    <div class="stats-grid">
      <div v-for="stat in profileStats" :key="stat.label" class="stat-card">
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

        <div v-for="match in recentMatches" :key="match.opponent" class="match-row">
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
</template>
