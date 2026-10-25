<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { settings } from '../settings.js'

const router = useRouter()

const ICONS = '/design/tac2-extra-icons.svg' // icon file in public/design

const modes = [
  {
    icon: 'friends',
    title: 'Pass & play',
    subtitle: 'Two players, one screen',
    note: 'Perfect for the sofa',
    theme: 'coral',
    detail: 'Take turns on the same device with a friend or family member.',
  },
  {
    icon: 'bot',
    title: 'Challenge Mochi',
    subtitle: 'Play against the computer',
    note: '3 difficulty levels',
    theme: 'teal',
    detail: 'Test your strategy against Mochi at three levels of cleverness.',
  },
  {
    icon: 'globe',
    title: 'Online room',
    subtitle: 'Play a friend from anywhere',
    note: 'Create or join a room',
    theme: 'violet',
    detail: 'Create a room code and share it — your friend joins in seconds.',
  },
]

const levels = [
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Cozy' },
  { value: 'hard', label: 'Tricky' },
]

const selected = ref(1) // index of the chosen mode
const difficulty = ref(settings.difficulty) // starts with the level from Settings
const onlineTab = ref('create') // 'create' | 'join'
const joinCode = ref('')
const copied = ref(false)

// TODO: later the backend creates the room code
function makeCode() {
  const letters = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  return Array.from({ length: 6 }, () => letters[Math.floor(Math.random() * letters.length)]).join('')
}
const roomCode = ref(makeCode())

const setupTitle = computed(() =>
  selected.value === 0
    ? 'Ready to share the board?'
    : selected.value === 1
      ? 'Choose your challenge'
      : 'Set up your room'
)

const setupText = computed(() => {
  if (selected.value === 0) return 'Player two will use the same screen. Pass when prompted.'
  if (selected.value === 1) return 'Pick how clever Mochi should be.'
  return onlineTab.value === 'create'
    ? 'Share the code with your friend to invite them.'
    : 'Ask your friend for the 6-letter room code.'
})

const buttonText = computed(() => {
  if (selected.value !== 2) return 'Start game'
  return onlineTab.value === 'join' ? 'Join room' : 'Create room'
})

const canStart = computed(
  () => !(selected.value === 2 && onlineTab.value === 'join' && joinCode.value.length !== 6)
)

const clockText = computed(() =>
  settings.clockMinutes === 0 ? 'no clock' : settings.clockMinutes + ' min each'
)

async function copyCode() {
  try {
    await navigator.clipboard.writeText(roomCode.value)
  } catch {
    // The browser may block the clipboard. The code is still on screen.
  }
  copied.value = true
  setTimeout(() => (copied.value = false), 1800)
}

function start() {
  if (!canStart.value) return

  if (selected.value === 0) {
    router.push('/play/local')
  } else if (selected.value === 1) {
    router.push({ path: '/play/computer', query: { level: difficulty.value } })
  } else {
    const room = onlineTab.value === 'create' ? roomCode.value : joinCode.value
    router.push({ path: '/play/online', query: { room } })
  }
}
</script>

<template>
  <section class="play-page">
    <div class="center-heading">
      <p class="eyebrow">Settle in</p>
      <h1>How would you like to play?</h1>
      <p class="subtitle">Pick a mode. You can change the details before the first move.</p>
    </div>

    <!-- Mode cards -->
    <div class="mode-grid">
      <button
        v-for="(mode, index) in modes"
        :key="mode.title"
        type="button"
        class="mode-card"
        :class="[mode.theme, { selected: selected === index }]"
        @click="selected = index"
      >
        <span class="mode-check">{{ selected === index ? '✓' : '' }}</span>
        <span class="mode-illustration">
          <svg class="icon"><use :href="ICONS + '#' + mode.icon" /></svg>
        </span>
        <span class="mode-title">{{ mode.title }}</span>
        <span class="mode-subtitle">{{ mode.subtitle }}</span>
        <span class="mode-detail">{{ mode.detail }}</span>
        <span class="mode-note">
          <svg class="icon"><use :href="ICONS + '#spark'" /></svg>
          {{ mode.note }}
        </span>
      </button>
    </div>

    <!-- Setup bar -->
    <div class="game-setup">
      <div class="setup-copy">
        <h2>{{ setupTitle }}</h2>
        <p>{{ setupText }}</p>
      </div>

      <!-- Difficulty (vs Mochi) -->
      <div v-if="selected === 1" class="segmented">
        <button
          v-for="level in levels"
          :key="level.value"
          type="button"
          :class="{ chosen: difficulty === level.value }"
          @click="difficulty = level.value"
        >
          {{ level.label }}
        </button>
      </div>

      <!-- Online room -->
      <div v-if="selected === 2" class="online-setup">
        <div class="segmented violet">
          <button type="button" :class="{ chosen: onlineTab === 'create' }" @click="onlineTab = 'create'">
            Create room
          </button>
          <button type="button" :class="{ chosen: onlineTab === 'join' }" @click="onlineTab = 'join'">
            Join room
          </button>
        </div>

        <div v-if="onlineTab === 'create'" class="room-display">
          <span class="room-code-label">Share this code</span>
          <strong class="room-code-big">{{ roomCode }}</strong>
          <button type="button" class="copy-code-btn" :class="{ copied }" @click="copyCode">
            {{ copied ? 'Copied!' : 'Copy code' }}
          </button>
        </div>

        <input
          v-else
          :value="joinCode"
          class="room-join-input"
          placeholder="Enter 6-letter code…"
          maxlength="6"
          autocomplete="off"
          @input="joinCode = $event.target.value.toUpperCase().slice(0, 6)"
        />
      </div>

      <button type="button" class="button start-button" :disabled="!canStart" @click="start">
        {{ buttonText }}
        <svg class="icon"><use :href="ICONS + '#arrow'" /></svg>
      </button>
    </div>

    <p class="note">
      Clock: <strong>{{ clockText }}</strong> ·
      <RouterLink to="/settings">change in settings</RouterLink> ·
      <RouterLink to="/how-to-play">how to play</RouterLink>
    </p>
  </section>
</template>

<style scoped>
.play-page {
  padding-bottom: 24px;
}

.center-heading {
  padding: 54px 0 36px;
  text-align: center;
}

.center-heading .eyebrow {
  margin-bottom: 0;
  color: var(--teal);
  font-size: 11px;
  letter-spacing: 2.4px;
}

.center-heading h1 {
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

/* ----- Mode cards ----- */
.mode-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 22px;
}

.mode-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 305px;
  padding: 32px;
  border: 2px solid transparent;
  border-radius: 26px;
  background: var(--paper);
  box-shadow: 0 10px 35px rgba(56, 70, 61, 0.06);
  color: var(--ink);
  font: inherit;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.mode-card:hover {
  transform: translateY(-4px);
}

.mode-card.selected.coral {
  border-color: var(--coral);
}

.mode-card.selected.teal {
  border-color: var(--teal);
}

.mode-card.selected.violet {
  border-color: var(--violet);
}

.mode-check {
  position: absolute;
  top: 16px;
  right: 16px;
  display: grid;
  place-items: center;
  width: 23px;
  height: 23px;
  border: 1px solid var(--line);
  border-radius: 50%;
  color: white;
  font-size: 12px;
}

.selected.coral .mode-check {
  border-color: var(--coral);
  background: var(--coral);
}

.selected.teal .mode-check {
  border-color: var(--teal);
  background: var(--teal);
}

.selected.violet .mode-check {
  border-color: var(--violet);
  background: var(--violet);
}

.mode-illustration {
  display: grid;
  place-items: center;
  width: 88px;
  height: 88px;
  margin: 8px auto 24px;
  border-radius: var(--radius-lg);
  transform: rotate(-3deg);
}

.coral .mode-illustration {
  background: var(--coral-soft);
  color: var(--coral);
}

.teal .mode-illustration {
  background: var(--teal-soft);
  color: var(--teal);
}

.violet .mode-illustration {
  background: var(--violet-soft);
  color: var(--violet);
}

.mode-illustration svg {
  width: 34px;
  height: 34px;
}

.mode-title {
  font-family: var(--font-title);
  font-size: 24px;
  font-weight: 700;
}

.mode-subtitle {
  margin-top: 7px;
  color: var(--muted);
  font-size: 14px;
}

.mode-detail {
  max-width: 220px;
  margin-top: 8px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.5;
}

.mode-note svg {
  width: 16px;
  height: 16px;
}

.mode-note {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: auto;
  padding-top: 20px;
  color: var(--muted);
  font-size: 12px;
}

/* ----- Setup bar ----- */
.game-setup {
  display: flex;
  align-items: center;
  gap: 28px;
  min-height: 94px;
  margin: 24px 0 20px;
  padding: 19px 24px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--paper);
}

.setup-copy {
  margin-right: auto;
}

.setup-copy h2 {
  font-family: var(--font-title);
  font-size: 19px;
}

.setup-copy p {
  margin-top: 4px;
  color: var(--muted);
  font-size: 12px;
}

/* Little switch with 2-3 options */
.segmented {
  display: flex;
  padding: 4px;
  border-radius: var(--radius-sm);
  background: var(--cream);
}

.segmented button {
  padding: 9px 15px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: var(--muted);
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.segmented .chosen {
  background: var(--paper);
  color: var(--teal);
  box-shadow: 0 3px 10px rgba(41, 59, 58, 0.09);
}

.segmented.violet .chosen {
  color: var(--violet);
}

/* Online */
.online-setup {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.room-display {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 3px;
}

.room-code-label {
  color: var(--muted);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.room-code-big {
  color: var(--violet);
  font-family: var(--font-title);
  font-size: 24px;
  letter-spacing: 4px;
}

.copy-code-btn {
  margin-top: 3px;
  padding: 6px 14px;
  border: 0;
  border-radius: 9px;
  background: var(--violet-soft);
  color: var(--violet);
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.copy-code-btn.copied {
  background: var(--teal-soft);
  color: var(--teal);
}

.room-join-input {
  height: 42px;
  padding: 0 14px;
  border: 1.5px solid var(--line);
  border-radius: 12px;
  background: var(--paper);
  color: var(--ink);
  font: inherit;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 2px;
  outline: none;
  text-transform: uppercase;
}

.room-join-input:focus {
  border-color: var(--violet);
}

.room-join-input::placeholder {
  font-size: 12px;
  font-weight: 400;
  letter-spacing: 0;
  text-transform: none;
}

.start-button {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 14px 22px;
  border: 0;
  font: inherit;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}

.start-button svg {
  width: 20px;
  height: 20px;
}

.start-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.note {
  color: var(--muted);
  font-size: 13px;
  text-align: center;
}

.note a {
  color: var(--teal-dark);
  font-weight: 700;
  text-decoration: underline;
}

/* ----- Small screens ----- */
@media (max-width: 760px) {
  .mode-grid {
    grid-template-columns: 1fr;
  }

  .mode-card {
    min-height: 255px;
  }

  .game-setup {
    align-items: stretch;
    flex-direction: column;
  }

  .segmented {
    justify-content: center;
  }

  .start-button {
    justify-content: center;
    width: 100%;
  }
}

@media (max-width: 460px) {
  .mode-card {
    padding: 25px;
  }
}
</style>