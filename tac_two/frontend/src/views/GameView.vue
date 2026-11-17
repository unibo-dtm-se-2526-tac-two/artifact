<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import { settings } from '../settings.js'
import { useAuthStore } from '../stores/auth'
import SettingsView from './SettingsView.vue'

const showSettings = ref(false)
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

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

// The name comes from the account you signed in with (the Play pages need a
// sign-in). The name typed in Settings is only the fallback.
const playerName = computed(
  () => authStore.user?.username || settings.playerName || 'Player 1',
)
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

const symbols = computed(() =>
  settings.markStyle === 'cozy' ? { X: '🐾', O: '🍃' } : { X: '×', O: '○' },
)

const markNames = computed(() =>
  settings.markStyle === 'cozy' ? { X: 'Paws', O: 'Leaves' } : { X: 'Crosses', O: 'Noughts' },
)

/* ---------------------------------------------------------------------------
   THE GAME ENGINE (Python backend)
   The backend knows the rules, the clock and the computer player.
   The frontend only shows what the backend sends and asks it to play moves:
     POST /api/v1/games              -> start a new game
     POST /api/v1/games/{id}/moves   -> play a move
     GET  /api/v1/games/{id}         -> read the game again
--------------------------------------------------------------------------- */

// The game sent by the backend (null until it arrives)
const game = ref(null)
const errorText = ref('')
const busy = ref(false) // true while we wait for the backend

// When this is not null the game cannot go on and the board is blocked:
//   'expired' -> the sign-in is no longer valid (the login lasts one hour)
//   'lost'    -> the backend does not know this game any more (for example it
//                was restarted: games live only in the server memory)
const problem = ref(null)

// An error that remembers the HTTP status of the answer (404, 409...)
class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

// Send a request to the game API. The token tells the backend who we are,
// so finished games are saved in our profile.
async function callApi(path, options = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (authStore.token) headers.Authorization = `Bearer ${authStore.token}`

  let response
  try {
    response = await fetch(`/api/v1/games${path}`, { ...options, headers })
  } catch {
    throw new ApiError('Cannot reach the game server. Is the backend running?', 0)
  }

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new ApiError(
      typeof data.detail === 'string' ? data.detail : 'Something went wrong.',
      response.status,
    )
  }
  return data
}

// Decide what a failed request means for the game
async function handleFailure(error) {
  if (error.status === 401 || error.status === 403) {
    // The backend does not accept our token. Ask who we are: if the token is
    // really dead the store signs us out, and we show the "sign in again" popup.
    const stillSignedIn = await authStore.fetchUser()
    problem.value = stillSignedIn ? 'lost' : 'expired'
  } else if (error.status === 404) {
    problem.value = 'lost'
  } else {
    errorText.value = error.message
  }
}

// Remember the new game and the moment we received it (the clock needs it)
let receivedAt = Date.now()
function setGame(data) {
  game.value = data
  receivedAt = Date.now()
}

// Open an empty board. The game is NOT created in the backend yet: the backend
// starts the clock the moment a game is created, so we create it when the
// player makes the FIRST MOVE (see playMove). Until then nothing is running
// and there is nothing to lose.
function startGame() {
  game.value = null
  errorText.value = ''
  problem.value = null
  leavesEarned.value = null
}

// Ask the backend for a new game (this is the moment the clock starts).
// Gives true when the game exists.
async function createGame() {
  // Online rooms are not in the backend yet
  if (isOnline.value) return false

  const body = {
    mode: mode.value,
    minutes: Number(settings.clockMinutes) || 0, // 0 = no clock
  }

  if (isComputer.value) {
    const level = route.query.level || settings.difficulty
    body.difficulty = ['easy', 'medium', 'hard'].includes(level) ? level : 'medium'
  }

  try {
    setGame(await callApi('', { method: 'POST', body: JSON.stringify(body) }))
    return true
  } catch (error) {
    await handleFailure(error)
    return false
  }
}

async function refreshGame() {
  if (!game.value) return
  try {
    setGame(await callApi(`/${game.value.id}`))
  } catch (error) {
    await handleFailure(error)
  }
}

// Can the player click this cell right now?
function canPlay(boardId, cellId) {
  if (busy.value || problem.value) return false

  const g = game.value

  // Empty board, nobody has played yet: any cell is free (except online rooms)
  if (!g) return !isOnline.value

  if (g.status !== 'playing') return false

  // Against the computer you only play when it is your turn
  if (g.mode === 'computer' && g.current_player !== g.human_player) return false

  if (g.board_winners[boardId] !== null) return false // this board is finished
  if (g.boards[boardId][cellId] !== null) return false // the cell is taken

  // The last move decides where you must play (null = free choice)
  return g.forced_board === null || g.forced_board === boardId
}

async function playMove(boardId, cellId) {
  if (!canPlay(boardId, cellId)) return

  busy.value = true
  errorText.value = ''

  try {
    // First move of the game: create the game now, so the clock starts now
    if (!game.value && !(await createGame())) return

    // Show our mark at once: the computer's answer can take a moment
    game.value.boards[boardId][cellId] = game.value.current_player

    try {
      const body = JSON.stringify({ board: boardId, cell: cellId })
      setGame(await callApi(`/${game.value.id}/moves`, { method: 'POST', body }))
    } catch (error) {
      // The move did NOT happen: take our mark back, so the board never shows
      // moves that the backend does not know.
      game.value.boards[boardId][cellId] = null

      if (error.status === 409) {
        // The rules said no (an illegal move, or the time was over): ask the
        // backend for the real situation.
        errorText.value = error.message
        await refreshGame()
      } else {
        await handleFailure(error)
      }
    }
  } finally {
    busy.value = false
  }
}

/* ---------------------------------------------------------------------------
   WHAT THE PAGE SHOWS
--------------------------------------------------------------------------- */

// Whose turn it is: 'X', 'O' or null (no game yet, or game over)
const currentTurn = computed(() => game.value?.current_player ?? null)

// While Mochi answers (the request is still running) the "To move" tag is on Mochi
const displayTurn = computed(() => {
  if (!game.value) return isOnline.value ? null : 'X' // empty board: X starts
  return isComputer.value && busy.value ? 'O' : currentTurn.value
})

const isWaiting = computed(() => isOnline.value && !hasOpponent.value)
const isThinking = computed(() => isComputer.value && displayTurn.value === 'O')

// The 9 boards with their 9 cells, taken from the backend game.
// With no game yet (or in online mode) the boards are empty.
const boards = computed(() =>
  Array.from({ length: 9 }, (_, boardId) => ({
    id: boardId,
    winner: game.value?.board_winners[boardId] ?? null, // 'X' | 'O' | 'draw' | null
    cells: Array.from({ length: 9 }, (_, cellId) => ({
      id: cellId,
      mark: game.value?.boards[boardId][cellId] ?? '',
    })),
  })),
)

// Green glow on the boards where the player is allowed to play
function isActiveBoard(board) {
  if (!settings.highlightBoards || problem.value) return false
  if (!game.value) return !isOnline.value // empty board: every board is free
  if (game.value.status !== 'playing') return false
  if (game.value.mode === 'computer' && currentTurn.value !== game.value.human_player) {
    return false
  }
  if (board.winner !== null) return false
  return game.value.forced_board === null || game.value.forced_board === board.id
}

// The newest move gets a small outline
function isLastMove(boardId, cellId) {
  const last = game.value?.last_moves?.at(-1)
  return Boolean(last) && last.board === boardId && last.cell === cellId
}

// Boards won so far (for the three dots)
const boardsWon = computed(() => {
  const winners = game.value?.board_winners ?? []
  return {
    X: winners.filter((w) => w === 'X').length,
    O: winners.filter((w) => w === 'O').length,
  }
})

// The clock. The backend sends the seconds left when it answered; between two
// answers we count down here so the numbers move.
//
// Only the player who is on turn loses time. Against the computer the answer of
// Mochi is calculated inside the same request as your move, so Mochi's clock
// only loses the (very short) time it really needed to think.
const now = ref(Date.now())
let timerId = null
let checkingTime = false

function secondsLeft(player) {
  const clock = game.value?.clock
  if (!clock) return null

  let left = player === 'X' ? clock.x : clock.o
  if (clock.active === player && game.value.status === 'playing' && !problem.value) {
    left -= (now.value - receivedAt) / 1000
  }
  return Math.max(0, left)
}

function formatTime(seconds) {
  if (seconds === null) return '∞'
  const total = Math.ceil(seconds)
  const minutes = String(Math.floor(total / 60)).padStart(2, '0')
  const rest = String(total % 60).padStart(2, '0')
  return `${minutes}:${rest}`
}

const timeX = computed(() => {
  if (!game.value) return startingTime.value
  return formatTime(secondsLeft('X'))
})

const timeO = computed(() => {
  if (!game.value) return startingTime.value
  return formatTime(secondsLeft('O'))
})

// Shown before the game arrives
const startingTime = computed(() => {
  const minutes = Number(settings.clockMinutes)
  if (minutes === 0) return '∞'
  return `${String(minutes || 5).padStart(2, '0')}:00`
})

// Every quarter of a second: move the clock, and if somebody ran out of time
// ask the backend, which is the one that ends the game.
async function tick() {
  now.value = Date.now()

  const g = game.value
  if (!g || g.status !== 'playing' || !g.clock || checkingTime || busy.value || problem.value) {
    return
  }

  if (secondsLeft(g.clock.active) <= 0) {
    checkingTime = true
    try {
      await refreshGame()
    } finally {
      checkingTime = false
    }
  }
}

// The text shown when the game is over
const resultText = computed(() => {
  const g = game.value
  if (!g || g.status !== 'finished') return ''

  const byTime = g.end_reason === 'timeout' ? ' on time' : ''

  if (!g.winner) return 'It’s a draw!'

  if (g.mode === 'computer') {
    return g.winner === g.human_player ? `You win${byTime}! 🎉` : `Mochi wins${byTime}.`
  }

  const name = g.winner === 'X' ? playerName.value : 'Player 2'
  return `${name} wins${byTime}! 🎉`
})

const mochiMessage = computed(() => {
  if (isWaiting.value) {
    return {
      main: 'Waiting for your friend!',
      detail: 'The game starts when your opponent joins.',
    }
  }

  if (resultText.value) {
    return { main: resultText.value, detail: 'Want to play again?' }
  }

  if (isThinking.value) {
    return {
      main: 'Now it’s my turn!',
      detail: 'Let me think about my next move...',
    }
  }

  if (!game.value && !isOnline.value) {
    return {
      main: 'Your turn! Ready, set, play!',
      detail: 'The clock starts with your first move.',
    }
  }

  return {
    main: 'Your turn! Ready, set, play!',
    detail: 'Choose an empty square in the highlighted board.',
  }
})

/* ---------------------------------------------------------------------------
   LEAVES EARNED
   When a game ends the backend saves it, and the leaves are worked out from the
   saved games. We read the profile again and show the difference.
--------------------------------------------------------------------------- */
const leavesEarned = ref(null)

watch(
  () => game.value?.status,
  async (status, before) => {
    // only when we SEE the game end (not when a finished game is simply loaded)
    if (status !== 'finished' || before !== 'playing') return
    if (!authStore.isAuthenticated) return

    const leavesBefore = authStore.profile?.leaves ?? 0
    const profile = await authStore.fetchProfile()
    if (profile && isComputer.value) leavesEarned.value = profile.leaves - leavesBefore
  },
)

// Only games with a clock against Mochi are saved, so only those give leaves
const countsForLeaves = computed(
  () => isComputer.value && Boolean(game.value?.clock),
)

/* ---------------------------------------------------------------------------
   LEAVING THE GAME
   A game that is not finished is lost when you leave (the backend only saves
   finished games). So we ask first, in a popup.
--------------------------------------------------------------------------- */
const leaveDialog = ref(false)
let answerLeave = null // resolves the question of the router guard

// true while a game with at least one move is running
const gameInProgress = computed(() => {
  const g = game.value
  return Boolean(g) && g.status === 'playing' && g.move_count > 0 && !problem.value
})

function askToLeave() {
  leaveDialog.value = true
  return new Promise((resolve) => {
    answerLeave = resolve
  })
}

function closeLeaveDialog(leave) {
  leaveDialog.value = false
  if (answerLeave) answerLeave(leave)
  answerLeave = null
}

// Runs for EVERY way of leaving: the "Leave game" button, the menu, the
// browser back button...
onBeforeRouteLeave(() => {
  if (!gameInProgress.value) return true
  return askToLeave()
})

// The button just goes to the menu; the guard above shows the popup
function leaveGame() {
  router.push('/play')
}

// Closing or refreshing the browser tab: the browser shows its own warning
function warnBeforeUnload(event) {
  if (!gameInProgress.value) return
  event.preventDefault()
  event.returnValue = ''
}

// When the sign-in ended we start again from the login page and come back here
async function signInAgain() {
  await authStore.logout()
  router.push({ name: 'login', query: { redirect: route.fullPath } })
}

function onKeydown(event) {
  if (event.key === 'Escape' && leaveDialog.value) closeLeaveDialog(false)
}

onMounted(() => {
  startGame()
  timerId = window.setInterval(tick, 250)
  window.addEventListener('beforeunload', warnBeforeUnload)
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.clearInterval(timerId)
  window.removeEventListener('beforeunload', warnBeforeUnload)
  window.removeEventListener('keydown', onKeydown)
})

// Going from one game page to another starts a new game.
// (Leaving to a page that is not a game must NOT start one.)
watch(
  () => route.fullPath,
  () => {
    if (['/play/local', '/play/computer', '/play/online'].includes(route.path)) startGame()
  },
)
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
         Settings
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

    <!-- MESSAGES: error, online not ready, game over -->
    <p v-if="errorText" class="game-banner error">{{ errorText }}</p>

    <p v-else-if="isOnline" class="game-banner">
      Online rooms are coming soon. This board is only a preview.
    </p>

    <section v-else-if="resultText" class="game-banner result">
      <strong>{{ resultText }}</strong>
      <span v-if="leavesEarned > 0" class="leaves-earned">+{{ leavesEarned }} 🍃</span>
      <span v-else-if="isComputer && !countsForLeaves" class="result-note">
        No clock, so no leaves this time.
      </span>
      <button type="button" class="banner-button" @click="startGame">Play again</button>
      <button type="button" class="banner-button" @click="leaveGame">Back to menu</button>
    </section>

    <!-- GAME AREA -->
    <section class="game-layout">
      <!-- LEFT: YOU -->
      <div class="side-col">
        <article class="player-card player-one">
          <span v-if="displayTurn === 'X'" class="turn-tag">To move</span>

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
              <strong>{{ timeX }}</strong>
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
              :class="{ 'active-board': isActiveBoard(board) }"
            >
              <button
                v-for="cell in board.cells"
                :key="cell.id"
                type="button"
                class="board-cell"
                :class="{
                  'mark-x': cell.mark === 'X',
                  'mark-o': cell.mark === 'O',
                  'last-move': isLastMove(board.id, cell.id),
                }"
                :disabled="!canPlay(board.id, cell.id)"
                @click="playMove(board.id, cell.id)"
              >
                {{ symbols[cell.mark] }}
              </button>

              <!-- Big mark on top of a finished board -->
              <div
                v-if="board.winner"
                class="board-result"
                :class="'result-' + board.winner"
              >
                {{ board.winner === 'draw' ? '–' : symbols[board.winner] }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT: OPPONENT AND MOCHI -->
      <div class="side-col">
        <article class="player-card player-two">
          <span v-if="displayTurn === 'O'" class="turn-tag">To move</span>

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
              <strong>{{ timeO }}</strong>
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

    <!-- POPUP: do you really want to leave? (the unfinished game would be lost) -->
    <div v-if="leaveDialog" class="dialog-backdrop" @click.self="closeLeaveDialog(false)">
      <section
        class="dialog leave-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="leave-title"
      >
        <img class="dialog-mochi" src="/design/mochi-mascot.svg" alt="" />
        <h2 id="leave-title">Leave this game?</h2>
        <p>
          If you leave now, <strong>your progress in this game will be lost</strong>. A game
          that is not finished is not saved, so it will not give you leaves or count in your
          statistics.
        </p>
        <div class="dialog-actions">
          <button type="button" class="dialog-button primary" @click="closeLeaveDialog(false)">
            Keep playing
          </button>
          <button type="button" class="dialog-button danger" @click="closeLeaveDialog(true)">
            Leave game
          </button>
        </div>
      </section>
    </div>

    <!-- POPUP: the game cannot go on (sign-in ended, or the backend lost the game) -->
    <div v-if="problem" class="dialog-backdrop">
      <section
        class="dialog problem-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="problem-title"
      >
        <img class="dialog-mochi" src="/design/mochi-mascot.svg" alt="" />
        <h2 id="problem-title">
          {{ problem === 'expired' ? 'Your sign-in has ended' : 'This game is no longer available' }}
        </h2>

        <p v-if="problem === 'expired'">
          The sign-in lasts one hour. Your last move was not played. Please sign in again to
          start a new game.
        </p>
        <p v-else>
          The game server does not know this game any more (it may have been restarted). Your
          last move was not played. Start a new game to keep playing.
        </p>

        <div class="dialog-actions">
          <button
            v-if="problem === 'expired'"
            type="button"
            class="dialog-button primary"
            @click="signInAgain"
          >
            Sign in again
          </button>

          <template v-else>
            <button type="button" class="dialog-button primary" @click="startGame">
              New game
            </button>
            <button type="button" class="dialog-button" @click="leaveGame">
              Back to menu
            </button>
          </template>
        </div>
      </section>
    </div>

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

.settings-button:hover {
  background: var(--line);
  color: var(--ink);
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

/* ---------- Cells are buttons now ---------- */

.board-cell {
  padding: 0;
  border: 0;
  cursor: default;
}

.board-cell:not(:disabled) {
  cursor: pointer;
}

.board-cell:not(:disabled):hover {
  background: var(--teal-soft);
}

.board-cell.last-move {
  outline: 2px solid var(--gold);
  outline-offset: -2px;
}

/* ---------- Finished board: big mark on top ---------- */

.mini-board {
  position: relative;
}

.board-result {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  border-radius: inherit;
  background: rgba(255, 255, 255, 0.86);
  font-family: var(--font-title);
  font-size: clamp(30px, 18cqmin, 120px);
  font-weight: 800;
  line-height: 1;
}

.board-result.result-X {
  color: var(--coral);
}

.board-result.result-O {
  color: var(--teal);
}

.board-result.result-draw {
  color: var(--muted);
}

/* ---------- Message bar (error, online preview, game over) ---------- */

.game-banner {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 12px;
  margin: 0;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  background: var(--teal-soft);
  color: var(--teal-dark);
  font-size: 14px;
}

.game-banner.error {
  background: var(--coral-soft);
  color: var(--danger);
}

.game-banner.result strong {
  margin-right: auto;
  font-family: var(--font-title);
  font-size: 18px;
}

.banner-button {
  padding: 7px 14px;
  border: 0;
  border-radius: var(--radius-pill);
  background: var(--paper);
  color: var(--teal-dark);
  font: inherit;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.banner-button:hover {
  background: var(--line);
}

.leaves-earned {
  padding: 4px 12px;
  border-radius: var(--radius-pill);
  background: var(--gold-soft);
  color: var(--gold-text);
  font-size: 13px;
  font-weight: 700;
}

.result-note {
  color: var(--muted);
  font-size: 13px;
}

/* POPUPS (leave the game, sign-in ended, game lost) */

.dialog-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1100;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgba(41, 59, 58, 0.45);
}

.dialog {
  width: min(100%, 420px);
  padding: 28px 28px 24px;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--paper);
  box-shadow: var(--shadow);
  text-align: center;
}

.dialog-mochi {
  display: block;
  width: 84px;
  height: 84px;
  margin: 0 auto 10px;
  object-fit: contain;
}

.dialog h2 {
  margin-bottom: 10px;
  font-family: var(--font-title);
  font-size: 24px;
  line-height: 1.2;
}

.dialog p {
  color: var(--muted);
  font-size: 14px;
  line-height: 1.6;
}

.dialog p strong {
  color: var(--ink);
}

.dialog-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 22px;
}

.dialog-button {
  min-width: 130px;
  padding: 11px 18px;
  border: 1px solid var(--line);
  border-radius: var(--radius-pill);
  background: var(--paper);
  color: var(--ink);
  font: inherit;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.dialog-button:hover {
  background: var(--line);
}

.dialog-button.primary {
  border-color: var(--teal);
  background: var(--teal);
  color: white;
}

.dialog-button.primary:hover {
  background: var(--teal-dark);
}

.dialog-button.danger {
  border-color: var(--coral-soft);
  background: var(--coral-soft);
  color: var(--danger);
}

.dialog-button.danger:hover {
  background: var(--coral);
  color: white;
}
</style>