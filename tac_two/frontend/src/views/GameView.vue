
<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { settings } from '../settings.js'
import SettingsView from './SettingsView.vue'

const showSettings = ref(false)
const route = useRoute()
const router = useRouter()

const ICONS = '/design/tac2-interface-icons.svg'
const EXTRA_ICONS = '/design/tac2-extra-icons.svg'

const mode = computed(() => {
  if (route.path === '/play/local') return 'local'
  if (route.path === '/play/online') return 'online'
  return 'computer'
})

const isLocal = computed(() => mode.value === 'local')
const isOnline = computed(() => mode.value === 'online')
const isComputer = computed(() => mode.value === 'computer')

const playerName = computed(() => settings.playerName || 'Player 1')
const hasOpponent = computed(() => Boolean(route.query.opponent))

const opponentName = computed(() => {
  if (isLocal.value) return 'Player 2'
  if (isComputer.value) return 'Mochi'
  return route.query.opponent || 'Waiting for player'
})

const roomCode = computed(() => route.query.room || '------')

const playerOneLabel = computed(() => (isLocal.value ? 'Player 1' : 'You'))

const playerTwoLabel = computed(() => {
  if (isLocal.value) return 'Player 2'
  if (isOnline.value) return 'Opponent'
  return 'Computer'
})

const startingTime = computed(() => {
  const minutes = Number(settings.clockMinutes)
  if (minutes === 0) return '∞'
  return `${String(minutes || 5).padStart(2, '0')}:00`
})

const symbols = computed(() =>
  settings.markStyle === 'cozy' ? { X: '🐾', O: '🍃' } : { X: '×', O: '○' },
)

const markNames = computed(() =>
  settings.markStyle === 'cozy' ? { X: 'Paws', O: 'Leaves' } : { X: 'Crosses', O: 'Noughts' },
)

// Current turn
// LATER: the game engine should update this value.
const currentTurn = ref('X')

const isYourTurn = computed(() => currentTurn.value === 'X')
const isWaiting = computed(() => isOnline.value && !hasOpponent.value)

const mochiMessage = computed(() => {
  if (isWaiting.value) {
    return {
      main: 'Waiting for your friend!',
      detail: 'The game starts when your opponent joins.',
    }
  }

  if (isYourTurn.value) {
    return {
      main: 'Your turn! Ready, set, play!',
      detail: 'Choose an empty square in the highlighted board.',
    }
  }

  return {
    main: 'Now it’s my turn!',
    detail: 'Let me think about my next move...',
  }
})

// Boards won so far
const boardsWon = { X: 0, O: 0 }

// Demo position
const SHOW_DEMO_POSITION = true

const demoPosition = {
  4: { 4: 'X', 0: 'O', 8: 'O', 3: 'O' },
  0: { 4: 'X' },
  8: { 1: 'X' },
  1: { 2: 'O' },
  2: { 4: 'X' },
}

const boards = Array.from({ length: 9 }, (_, boardIndex) => ({
  id: boardIndex,
  cells: Array.from({ length: 9 }, (_, cellIndex) => ({
    id: cellIndex,
    mark: SHOW_DEMO_POSITION ? (demoPosition[boardIndex]?.[cellIndex] ?? '') : '',
  })),
}))

function leaveGame() {
  router.push('/play')
}
</script>

<template>
  <main class="game-page">
    <!-- HEADER -->
    <header class="game-header">
      <button class="leave-button" @click="leaveGame">
        <svg class="icon back-icon">
          <use :href="EXTRA_ICONS + '#arrow'" />
        </svg>
        Leave game
      </button>

      <div class="header-right">
        <button
  class="settings-button"
  aria-label="Settings"
  @click="showSettings = true"
>
          ⚙
        </button>
      </div>
    </header>

    <!-- ONLINE ROOM -->
    <section v-if="isOnline" class="room-strip">
      <svg class="icon">
        <use :href="ICONS + '#online'" />
      </svg>
      <span class="room-label">Room</span>
      <strong class="room-code">{{ roomCode }}</strong>
      <p>
        {{ hasOpponent ? `${opponentName} is in the room.` : 'Share this code with your friend.' }}
      </p>
    </section>

    <!-- GAME AREA -->
    <section class="game-layout">
      <!-- LEFT: YOU -->
      <div class="side-col">
        <article class="player-card player-one">
          <span class="turn-tag">To move</span>

          <div class="player-main">
            <div class="player-avatar">{{ symbols.X }}</div>

            <div class="player-details">
              <span class="player-role">{{ playerOneLabel }}</span>
              <strong>{{ playerName }}</strong>
              <small>{{ markNames.X }} · X</small>
            </div>
          </div>

          <div class="player-stats">
            <div class="timer">
              <svg class="icon">
                <use :href="ICONS + '#clock'" />
              </svg>
              <strong>{{ startingTime }}</strong>
            </div>

            <div class="boards-won">
              <span>Boards won</span>
              <div class="pips">
                <i
                  v-for="n in 3"
                  :key="n"
                  class="pip"
                  :class="{ filled: n <= boardsWon.X }"
                ></i>
              </div>
            </div>
          </div>
        </article>
      </div>

      <!-- CENTRE: BOARD -->
      <div class="board-panel">
        <div class="board-stage">
          <div class="ultimate-board">
            <div
              v-for="board in boards"
              :key="board.id"
              class="mini-board"
              :class="{ 'active-board': board.id === 3 }"
            >
              <div
                v-for="cell in board.cells"
                :key="cell.id"
                class="board-cell"
                :class="{
                  'mark-x': cell.mark === 'X',
                  'mark-o': cell.mark === 'O',
                }"
              >
                {{ symbols[cell.mark] }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT: OPPONENT AND MOCHI -->
      <div class="side-col">
        <article class="player-card player-two">
          <div class="player-main">
            <div class="player-avatar">
              <img
                v-if="isComputer"
                class="mochi-img"
                src="/design/mochi-mascot.svg"
                alt="Mochi the cat"
              />
              <template v-else>{{ symbols.O }}</template>
            </div>

            <div class="player-details">
              <span class="player-role">{{ playerTwoLabel }}</span>
              <strong>{{ opponentName }}</strong>
              <small v-if="isOnline && !hasOpponent">Not connected yet</small>
              <small v-else>{{ markNames.O }} · O</small>
            </div>
          </div>

          <div class="player-stats">
            <div class="timer">
              <svg class="icon">
                <use :href="ICONS + '#clock'" />
              </svg>
              <strong>{{ startingTime }}</strong>
            </div>

            <div class="boards-won">
              <span>Boards won</span>
              <div class="pips">
                <i
                  v-for="n in 3"
                  :key="n"
                  class="pip"
                  :class="{ filled: n <= boardsWon.O }"
                ></i>
              </div>
            </div>
          </div>
        </article>

        <!-- MOCHI'S DYNAMIC MESSAGE -->
        <section v-if="isComputer || isOnline" class="mochi-says">
          <div class="mochi-pic">
            <img class="mochi-img" src="/design/mochi-mascot.svg" alt="" />
          </div>

          <div class="bubble">
            <strong>{{ mochiMessage.main }}</strong>
            <small>{{ mochiMessage.detail }}</small>
          </div>
        </section>

        <p v-else-if="isLocal" class="local-note">
          <svg class="icon">
            <use :href="ICONS + '#friends'" />
          </svg>
          Pass the device after each move.
        </p>
      </div>
    </section>

    <!-- SETTINGS POPUP -->
    <SettingsView
      :open="showSettings"
      @close="showSettings = false"
    />
  </main>
</template>

<style scoped>
.game-page {
  --app-header: 60px;

  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 1320px;
  height: calc(100dvh - var(--app-header));
  min-height: 480px;
  margin: 0 auto;
  padding: 10px 0 14px;
  color: var(--ink);
}

/* HEADER */

.game-header {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.leave-button {
  display: flex;
  align-items: center;
  gap: 6px;
  width: fit-content;
  padding: 8px 14px 8px 8px;
  border: 0;
  border-radius: var(--radius-pill);
  background: transparent;
  color: var(--muted);
  font: inherit;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.leave-button:hover {
  background: var(--line);
  color: var(--ink);
}

.back-icon {
  width: 18px;
  height: 18px;
  transform: rotate(180deg);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.settings-button {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: var(--paper);
  color: var(--ink);
  font-size: 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.settings-button:hover {
  background: var(--line);
}

/* MOCHI IMAGE */

.mochi-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* ONLINE ROOM */

.room-strip {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  background: var(--violet-soft);
  color: var(--violet);
}

.room-strip .icon {
  width: 20px;
  height: 20px;
}

.room-label {
  font-size: 13px;
  font-weight: 600;
}

.room-code {
  font-family: var(--font-title);
  font-size: 18px;
  letter-spacing: 3px;
}

.room-strip p {
  margin: 0 0 0 auto;
  color: var(--muted);
  font-size: 13px;
}

/* GAME LAYOUT */

.game-layout {
  display: grid;
  flex: 1 1 0;
  min-height: 0;
  grid-template-columns: 216px minmax(0, 1fr) 216px;
  grid-template-rows: minmax(0, 1fr);
  gap: 18px;
}

.side-col {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 0;
  overflow: hidden;
}

/* BOARD PANEL */

.board-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  padding: 16px 20px 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--paper);
  box-shadow: var(--shadow);
}

/* BOARD STAGE */

.board-stage {
  display: grid;
  flex: 1 1 0;
  min-width: 0;
  min-height: 0;
  place-items: center;
  overflow: hidden;
  container-type: size;
}

/* ULTIMATE BOARD */

.ultimate-board {
  display: grid;
  width: min(100cqw, 100cqh);
  height: min(100cqw, 100cqh);
  max-width: 100%;
  max-height: 100%;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  grid-template-rows: repeat(3, minmax(0, 1fr));
  gap: clamp(3px, 1.1vmin, 6px);
  overflow: hidden;
}

.mini-board {
  display: grid;
  min-width: 0;
  min-height: 0;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  grid-template-rows: repeat(3, minmax(0, 1fr));
  gap: clamp(1px, 0.5vmin, 3px);
  padding: clamp(2px, 0.9vmin, 5px);
  border-radius: clamp(5px, 1.4vmin, 9px);
  background: var(--line);
}

.mini-board.active-board {
  outline: 3px solid var(--teal);
  outline-offset: -2px;
  box-shadow: 0 8px 20px rgba(47, 138, 127, 0.2);
}

.board-cell {
  display: grid;
  min-width: 0;
  min-height: 0;
  place-items: center;
  border-radius: 3px;
  background: var(--paper);
  font-family: var(--font-title);
  font-size: clamp(14px, 5cqmin, 42px);
  font-weight: 800;
  line-height: 1;
}

.board-cell.mark-x {
  color: var(--coral);
}

.board-cell.mark-o {
  color: var(--teal);
}

/* PLAYER CARDS */

.player-card {
  position: relative;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  gap: 14px;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--paper);
}

.player-one {
  --accent: var(--coral);
  --accent-soft: var(--coral-soft);

  border-color: var(--coral);
  box-shadow: 0 10px 28px rgba(233, 116, 97, 0.14);
}

.player-two {
  --accent: var(--teal);
  --accent-soft: var(--teal-soft);
}

.turn-tag {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 3px 9px;
  border-radius: var(--radius-pill);
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 11px;
  font-weight: 700;
}

.player-main {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.player-avatar {
  display: grid;
  flex: 0 0 52px;
  width: 52px;
  height: 52px;
  place-items: center;
  overflow: hidden;
  border-radius: 16px;
  background: var(--accent-soft);
  color: var(--accent);
  font-family: var(--font-title);
  font-size: 28px;
  font-weight: 800;
}

.player-details {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.player-role {
  color: var(--muted);
  font-size: 12px;
}

.player-details strong {
  overflow-wrap: anywhere;
  font-family: var(--font-title);
  font-size: 18px;
  font-weight: 700;
  line-height: 1.2;
}

.player-details small {
  margin-top: 1px;
  color: var(--muted);
  font-size: 12px;
}

.player-stats {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--line);
}

.timer {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

.timer .icon {
  width: 18px;
  height: 18px;
}

.timer strong {
  color: var(--ink);
  font-family: var(--font-title);
  font-size: 24px;
  font-weight: 700;
}

.boards-won {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  color: var(--muted);
  font-size: 11px;
}

.pips {
  display: flex;
  gap: 5px;
}

.pip {
  width: 12px;
  height: 12px;
  border: 2px solid var(--line);
  border-radius: 50%;
}

.pip.filled {
  border-color: var(--accent);
  background: var(--accent);
}

/* MOCHI'S SPEECH BUBBLE */

.mochi-says {
  display: flex;
  align-items: flex-end;
  gap: 6px;
}

.mochi-pic {
  flex: 0 0 68px;
  width: 68px;
  height: 68px;
}

.bubble {
  position: relative;
  min-width: 0;
  margin-bottom: 14px;
  padding: 11px 13px;
  border: 1px solid var(--line);
  border-radius: 16px 16px 16px 4px;
  background: var(--paper);
  font-size: 14px;
  line-height: 1.4;
}

.bubble strong {
  display: block;
  font-weight: 700;
}

.bubble small {
  display: block;
  margin-top: 4px;
  color: var(--teal-dark);
  font-size: 12px;
  font-weight: 600;
}

.local-note {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 4px;
  color: var(--muted);
  font-size: 13px;
}

.local-note .icon {
  flex: 0 0 auto;
  width: 18px;
  height: 18px;
}

/* SHORT SCREENS */

@media (max-height: 760px) {
  .game-page {
    gap: 8px;
    padding-top: 8px;
    padding-bottom: 10px;
  }

  .player-card {
    gap: 10px;
    padding: 12px;
  }

  .player-avatar {
    flex-basis: 44px;
    width: 44px;
    height: 44px;
    font-size: 24px;
  }

  .mochi-pic {
    flex-basis: 52px;
    width: 52px;
    height: 52px;
  }

  .bubble {
    margin-bottom: 8px;
    padding: 9px 10px;
    font-size: 13px;
  }
}

@media (max-height: 640px) {
  .mochi-says,
  .local-note {
    display: none;
  }
}

/* NARROWER SCREENS */

@media (max-width: 1100px) {
  .game-layout {
    grid-template-columns: 190px minmax(0, 1fr) 190px;
    gap: 12px;
  }

  .player-stats {
    flex-direction: column;
    align-items: flex-start;
  }

  .boards-won {
    align-items: flex-start;
  }
}

/* TABLETS AND PHONES */

@media (max-width: 900px) {
  .game-layout {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto minmax(0, 1fr);
    grid-template-areas:
      'one two'
      'board board';
    gap: 10px;
  }

  .side-col {
    display: contents;
  }

  .player-one {
    grid-area: one;
  }

  .player-two {
    grid-area: two;
  }

  .board-panel {
    grid-area: board;
    width: min(100%, calc(100dvh - 230px));
    aspect-ratio: 1 / 1;
    justify-self: center;
  }

  .side-col > :not(.player-card) {
    display: none;
  }

  .player-card {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 8px 10px;
  }

  .turn-tag,
  .boards-won,
  .player-role,
  .player-details small,
  .timer .icon {
    display: none;
  }

  .player-avatar {
    flex-basis: 38px;
    width: 38px;
    height: 38px;
    border-radius: 12px;
    font-size: 21px;
  }

  .player-details strong {
    font-size: 14px;
  }

  .player-stats {
    padding: 0;
    border: 0;
  }

  .timer strong {
    font-size: 18px;
  }
}

@media (max-width: 700px) {
  .game-header {
    gap: 8px;
  }

  .board-panel {
    padding: 10px;
  }
}

@media (max-width: 420px) {
  .player-main {
    gap: 8px;
  }

  .player-avatar {
    flex-basis: 32px;
    width: 32px;
    height: 32px;
    border-radius: 10px;
    font-size: 18px;
  }

  .player-details strong {
    font-size: 13px;
  }

  .board-panel {
    width: min(100%, calc(100dvh - 210px));
  }
}
</style>

<style>
.app:has(.game-page) {
  padding-bottom: 0;
}
</style>
