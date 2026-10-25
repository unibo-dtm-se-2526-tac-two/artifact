<script setup>
import { computed } from 'vue'

const EXTRA_ICONS = '/design/tac2-extra-icons.svg' // leaf icon lives here

// TODO: take this from the logged-in user
const currentUser = 'Sofia'

// TODO: later this list comes from the backend
const players = [
  { name: 'LunaLoops', initials: 'LL', leaves: 2840, winRate: 76 },
  { name: 'GridWizard', initials: 'GW', leaves: 2615, winRate: 72 },
  { name: 'TeaAndTactics', initials: 'TT', leaves: 2420, winRate: 69 },
  { name: 'CrossBoss', initials: 'CB', leaves: 2180, winRate: 67 },
  { name: 'Sofia', initials: 'S', leaves: 1240, winRate: 58 },
  { name: 'NoughtyCat', initials: 'NC', leaves: 1195, winRate: 56 },
]

// Players sorted from most to fewest leaves
const ranked = computed(() => [...players].sort((a, b) => b.leaves - a.leaves))

// The podium shows 2nd, 1st, 3rd (first place in the middle)
const podium = computed(() => [
  { place: 2, player: ranked.value[1] },
  { place: 1, player: ranked.value[0] },
  { place: 3, player: ranked.value[2] },
])
</script>

<template>
  <section class="leaderboard-page">
    <header class="leader-heading">
      <div>
        <p class="eyebrow">Hall of clever moves</p>
        <h1>The leaf board</h1>
        <p class="subtitle">Earn leaves by winning matches and climbing through the seasons.</p>
      </div>

      <div class="season-pill">
        <span>Spring season</span>
        <strong>12 days left</strong>
      </div>
    </header>

    <div class="podium">
      <div
        v-for="item in podium"
        :key="item.player.name"
        class="podium-player"
        :class="'place-' + item.place"
      >
        <div class="podium-avatar">
          {{ item.player.initials }}
          <span v-if="item.place === 1" class="crown">♢</span>
        </div>
        <strong class="podium-name">{{ item.player.name }}</strong>
       <span class="podium-leaves">{{ item.player.leaves.toLocaleString() }} 🍃</span>
        <div class="podium-block">{{ item.place }}</div>
      </div>
    </div>

    <div class="ranking-card">
      <div class="ranking-head">
        <span>Rank</span>
        <span>Player</span>
        <span>Win rate</span>
        <span>Leaves</span>
      </div>

      <div
        v-for="(player, index) in ranked"
        :key="player.name"
        class="ranking-row"
        :class="{ me: player.name === currentUser }"
      >
        <span>{{ index + 1 }}</span>

        <span class="ranking-user">
          <i>{{ player.initials }}</i>
          <strong>{{ player.name }}</strong>
          <small v-if="player.name === currentUser">You</small>
        </span>

        <span>{{ player.winRate }}%</span>
        <strong class="leaf-count">{{ player.leaves.toLocaleString() }} 🍃</strong>
      </div>
    </div>
  </section>
</template>

<style scoped>
.leaderboard-page {
  padding: 55px 0 70px;
}

.leader-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
}

.leader-heading .eyebrow {
  margin-bottom: 0;
  color: var(--teal);
  font-size: 11px;
  letter-spacing: 2.4px;
}

.leader-heading h1 {
  margin-top: 10px;
  font-family: var(--font-title);
  font-size: clamp(38px, 4vw, 52px);
  line-height: 1.08;
  letter-spacing: -1.7px;
}

.subtitle {
  margin-top: 12px;
  color: var(--muted);
  font-size: 15px;
}

.season-pill {
  display: flex;
  flex-direction: column;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  background: var(--gold-soft);
  color: var(--gold-text);
  white-space: nowrap;
}

.season-pill span {
  font-size: 11px;
}

.season-pill strong {
  margin-top: 2px;
  font-size: 13px;
}

/* ----- Podium ----- */
.podium {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 15px;
  height: 250px;
  margin-top: 35px;
}

.podium-player {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 150px;
  text-align: center;
}

.podium-avatar {
  position: relative;
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  border-radius: 20px;
  font-family: var(--font-title);
  font-size: 16px;
  font-weight: 700;
}

.podium-name {
  margin-top: 10px;
  font-family: var(--font-title);
  font-size: 14px;
}

.podium-leaves {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--muted);
  font-size: 12px;
}

.podium-leaves svg,
.leaf-count svg {
  width: 14px;
  height: 14px;
  color: var(--teal);
}

.leaf-count {
  display: flex;
  align-items: center;
  gap: 5px;
}

.podium-block {
  width: 100%;
  margin-top: 12px;
  padding-top: 17px;
  border-radius: 14px 14px 0 0;
  font-family: var(--font-title);
  font-size: 24px;
  font-weight: 700;
}

/* 1st place: gold, tallest */
.place-1 .podium-avatar {
  width: 70px;
  height: 70px;
  background: var(--gold-soft);
  color: var(--gold-text);
}

.place-1 .podium-block {
  height: 112px;
  background: var(--gold-soft);
}

/* 2nd place: violet */
.place-2 .podium-avatar {
  background: var(--violet-soft);
  color: var(--violet);
}

.place-2 .podium-block {
  height: 88px;
  background: var(--violet-soft);
}

/* 3rd place: coral, lowest */
.place-3 .podium-avatar {
  background: var(--coral-soft);
  color: var(--coral);
}

.place-3 .podium-block {
  height: 70px;
  background: var(--coral-soft);
}

.crown {
  position: absolute;
  top: -19px;
  color: var(--gold);
  font-size: 23px;
}

/* ----- Table ----- */
.ranking-card {
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--paper);
}

.ranking-head,
.ranking-row {
  display: grid;
  grid-template-columns: 70px 1fr 130px 110px;
  align-items: center;
  padding: 0 25px;
}

.ranking-head {
  height: 42px;
  background: var(--surface-alt);
  color: var(--muted);
  font-size: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.ranking-row {
  min-height: 59px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 13px;
}

.ranking-row.me {
  background: var(--teal-soft);
  color: var(--teal-dark);
}

.ranking-user {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  color: var(--ink);
}

.ranking-user i {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: var(--cream);
  font-size: 10px;
  font-style: normal;
}

.ranking-user strong {
  overflow-wrap: anywhere;
}

.ranking-user small {
  padding: 3px 7px;
  border-radius: 6px;
  background: white;
  color: var(--teal);
  font-size: 10px;
}

/* ----- Small screens ----- */
@media (max-width: 760px) {
  .leader-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 15px;
  }

  .ranking-head,
  .ranking-row {
    grid-template-columns: 42px 1fr 70px;
    padding: 0 12px;
  }

  /* hide the "Win rate" column on phones */
  .ranking-head span:nth-child(3),
  .ranking-row > span:nth-child(3) {
    display: none;
  }

  .podium-player {
    width: 30%;
  }
}

@media (max-width: 460px) {
  .podium {
    height: 210px;
  }

  .podium-name {
    font-size: 11px;
  }

  .podium-avatar {
    width: 46px;
    height: 46px;
  }

  .place-1 .podium-avatar {
    width: 55px;
    height: 55px;
  }
}
</style>