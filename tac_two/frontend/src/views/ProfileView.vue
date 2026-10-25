<script setup>
const ICONS = '/design/tac2-interface-icons.svg'
const EXTRA_ICONS = '/design/tac2-extra-icons.svg' // leaf icon lives here

const progress = 72 // percent of the way to the next level

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
    <div class="profile-banner surface">
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
      <div v-for="stat in profileStats" :key="stat.label" class="stat-card surface">
        <strong>{{ stat.value }}</strong>
        <span>{{ stat.label }}</span>
      </div>
    </div>

    <div class="dashboard-grid">
      <div class="dash-card surface">
        <div class="dash-title">
          <span>Your cozy progress</span>
          <strong>Level 7</strong>
        </div>

        <div class="level-row">
          <div class="level-badge">7</div>
          <div class="level-info">
            <strong>Tactical Tabby</strong>
            <span>260 🍃 to level 8</span>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: progress + '%' }"></div>
            </div>
          </div>
        </div>

        <div class="achievement-row">
          <div v-for="item in achievements" :key="item.label" class="achievement">
            <svg class="icon">
              <use :href="ICONS + '#' + item.icon" />
            </svg>
            <span>{{ item.label }}</span>
          </div>
        </div>
      </div>

      <div class="dash-card surface">
        <div class="dash-title history-title">
          <span>Recent matches</span>
          <strong>View all</strong>
        </div>

        <div
          v-for="match in recentMatches"
          :key="match.date + match.opponent"
          class="match-row"
        >
          <div class="match-symbol">×</div>

          <div class="match-info">
            <strong>{{ match.opponent }}</strong>
            <span>{{ match.date }}</span>
          </div>

          <small :class="match.result.toLowerCase()">{{ match.result }}</small>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.profile-page {
  padding: 56px 0 24px;
}

/* ----- Banner ----- */
.profile-banner {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 32px;
  margin-bottom: 24px;
  border-radius: var(--radius-lg);
}

.big-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 104px;
  height: 104px;
  overflow: hidden;
  border-radius: var(--radius-lg);
  background: var(--gold-soft);
}

.big-avatar img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.profile-main {
  flex: 1;
  min-width: 0;
}

.profile-main .eyebrow {
  margin-bottom: 8px;
}

.profile-main h1 {
  font-family: var(--font-title);
  font-size: clamp(32px, 4vw, 48px);
  line-height: 1.1;
}

.profile-meta {
  margin-top: 8px;
  color: var(--muted);
  font-size: 15px;
}

/* ----- Statistics ----- */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 24px;
  border-radius: var(--radius-md);
}

.stat-card strong {
  font-family: var(--font-title);
  font-size: 36px;
  line-height: 1.2;
}

.stat-card span {
  color: var(--muted);
  font-size: 15px;
}

/* ----- Progress and history cards ----- */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  align-items: start;
}

.dash-card {
  min-width: 0;
  padding: 26px;
  border-radius: var(--radius-lg);
}

.dash-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 24px;
  font-size: 17px;
}

.dash-title strong {
  color: var(--teal-dark);
  font-size: 14px;
}

.history-title {
  margin-bottom: 8px;
}

/* Level */
.level-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}

.level-badge {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 58px;
  height: 58px;
  border-radius: 20px;
  background: var(--gold-soft);
  font-family: var(--font-title);
  font-size: 28px;
  font-weight: 800;
}

.level-info {
  flex: 1;
  min-width: 0;
}

.level-info strong,
.level-info span {
  display: block;
}

.level-info span {
  margin-top: 4px;
  color: var(--muted);
  font-size: 13px;
}

.leaf-icon {
  width: 14px;
  height: 14px;
  vertical-align: -2px;
  color: var(--teal);
}

.progress-track {
  height: 8px;
  margin-top: 12px;
  overflow: hidden;
  border-radius: var(--radius-pill);
  background: var(--line);
}

.progress-fill {
  height: 100%;
  border-radius: inherit;
  background: var(--teal);
}

/* Achievements */
.achievement-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
}

.achievement {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 16px 6px;
  border-radius: var(--radius-md);
  background: var(--cream);
  text-align: center;
}

.achievement .icon {
  width: 24px;
  height: 24px;
  color: var(--teal-dark);
}

.achievement span {
  font-size: 12px;
  font-weight: 700;
}

/* Recent matches */
.match-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 0;
  border-bottom: 1px solid var(--line);
}

.match-row:last-child {
  border-bottom: 0;
}

.match-symbol {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  background: var(--coral-soft);
  color: var(--coral);
  font-size: 26px;
  font-weight: 700;
}

.match-info {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.match-info strong {
  font-size: 14px;
}

.match-info span {
  color: var(--muted);
  font-size: 13px;
}

.match-row small {
  font-size: 12px;
  font-weight: 700;
}

.match-row small.won {
  color: var(--teal-dark);
}

.match-row small.lost {
  color: var(--coral);
}

/* ----- Small screens ----- */
@media (max-width: 880px) {
  .profile-page {
    padding-top: 36px;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .profile-banner {
    flex-wrap: wrap;
    gap: 16px;
    padding: 22px;
  }

  .big-avatar {
    width: 76px;
    height: 76px;
    border-radius: var(--radius-md);
  }

  .profile-main {
    flex-basis: calc(100% - 100px);
  }

  .profile-main h1 {
    font-size: 30px;
    overflow-wrap: anywhere;
  }

  .profile-banner .secondary-action {
    margin-left: 92px;
  }

  .stats-grid {
    gap: 8px;
  }

  .stat-card {
    padding: 16px 10px;
    border-radius: var(--radius-sm);
  }

  .stat-card strong {
    font-size: 27px;
  }

  .stat-card span {
    font-size: 12px;
  }

  .dash-card {
    padding: 20px;
  }

  .achievement-row {
    gap: 6px;
  }

  .achievement span {
    font-size: 11px;
  }

  .match-row {
    gap: 10px;
  }
}
</style>