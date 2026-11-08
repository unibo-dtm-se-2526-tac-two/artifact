
<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { settings } from '../settings.js'

const router = useRouter()

const modes = [
  {
    icon: '♙',
    title: 'Pass & play',
    subtitle: 'Two players, one screen',
    note: 'Perfect for the sofa',
    theme: 'coral',
    detail: 'Take turns on the same device with a friend or family member.',
  },
  {
    icon: '✦',
    title: 'Challenge Mochi',
    subtitle: 'Play against the computer',
    note: 'A three-step cat challenge',
    theme: 'teal',
    detail: 'Test your strategy against Mochi at three levels of cleverness.',
  },
  {
    icon: '◎',
    title: 'Online room',
    subtitle: 'Play a friend from anywhere',
    note: 'Create or join a room',
    theme: 'violet',
    detail: 'Create a room code and share it with your friend.',
  },
]

const levels = [
  { value: 'easy', label: 'Kitten Steps' },
  { value: 'medium', label: 'Clever Paws' },
  { value: 'hard', label: 'Tiger Mode' },
]

const selected = ref(1)
const difficulty = ref(settings.difficulty || 'medium')
const onlineTab = ref('create')
const joinCode = ref('')
const copied = ref(false)

function makeCode() {
  const characters = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

  return Array.from({ length: 6 }, () =>
    characters[Math.floor(Math.random() * characters.length)],
  ).join('')
}

const roomCode = ref(makeCode())

const setupTitle = computed(() => {
  if (selected.value === 0) return 'Ready to share the board?'
  if (selected.value === 1) return 'Choose your challenge'
  return 'Set up your room'
})

const setupText = computed(() => {
  if (selected.value === 0) {
    return 'Player two will use the same screen. Pass when prompted.'
  }

  if (selected.value === 1) {
    return 'You can level up after a match.'
  }

  if (onlineTab.value === 'create') {
    return 'Share the code with your friend to invite them.'
  }

  return 'Ask your friend for the six-letter room code.'
})

const buttonText = computed(() => {
  if (selected.value === 2 && onlineTab.value === 'join') {
    return 'Join room'
  }

  if (selected.value === 2) {
    return 'Create room'
  }

  return 'Start game'
})

const canStart = computed(() => {
  if (selected.value === 2 && onlineTab.value === 'join') {
    return joinCode.value.trim().length === 6
  }

  return true
})

function selectMode(index) {
  selected.value = index
}

function selectDifficulty(value) {
  difficulty.value = value
  settings.difficulty = value
}

async function copyCode() {
  try {
    await navigator.clipboard.writeText(roomCode.value)
    copied.value = true
    window.setTimeout(() => {
      copied.value = false
    }, 1800)
  } catch (error) {
    console.error('Could not copy room code:', error)
    copied.value = false
  }
}

function start() {
  if (!canStart.value) return

  if (selected.value === 0) {
    router.push('/play/local')
    return
  }

  if (selected.value === 1) {
    router.push({
      path: '/play/computer',
      query: { level: difficulty.value },
    })
    return
  }

  const room =
    onlineTab.value === 'create'
      ? roomCode.value
      : joinCode.value.trim().toUpperCase()

  router.push({
    path: '/play/online',
    query: { room },
  })
}
</script>

<template>
  <div class="page play-page">
    <section class="center-heading">
      <div class="section-kicker">Settle in</div>

      <h1 class="page-title">How would you like to play?</h1>

      <p class="page-subtitle">
        Pick a mode. You can change the details before the first move.
      </p>
    </section>

    <section class="mode-grid">
      <button
        v-for="(mode, index) in modes"
        :key="mode.title"
        type="button"
        class="mode-card"
        :class="[
          mode.theme,
          { selected: selected === index },
        ]"
        :aria-pressed="selected === index"
        @click="selectMode(index)"
      >
        <span class="mode-check">
          {{ selected === index ? '✓' : '' }}
        </span>

        <span class="mode-illustration">
          {{ mode.icon }}
        </span>

        <span class="mode-title">{{ mode.title }}</span>

        <span class="mode-subtitle">{{ mode.subtitle }}</span>

        <span class="mode-detail">{{ mode.detail }}</span>

        <span class="mode-note">
          <span class="spark-icon">✧</span>
          {{ mode.note }}
        </span>
      </button>
    </section>

    <section class="game-setup">
      <div class="setup-copy">
        <h2 class="setup-title">{{ setupTitle }}</h2>
        <p class="setup-sub">{{ setupText }}</p>
      </div>

      <!-- Difficulty selection -->
      <div v-if="selected === 1" class="difficulty">
        <button
          v-for="level in levels"
          :key="level.value"
          type="button"
          :class="{ chosen: difficulty === level.value }"
          :aria-pressed="difficulty === level.value"
          @click="selectDifficulty(level.value)"
        >
          {{ level.label }}
        </button>
      </div>

      <!-- Online room setup -->
      <div v-if="selected === 2" class="online-setup">
        <div class="online-tabs-sm">
          <button
            type="button"
            :class="{ chosen: onlineTab === 'create' }"
            @click="onlineTab = 'create'"
          >
            Create room
          </button>

          <button
            type="button"
            :class="{ chosen: onlineTab === 'join' }"
            @click="onlineTab = 'join'"
          >
            Join room
          </button>
        </div>

        <div v-if="onlineTab === 'create'" class="room-display">
          <span class="room-code-label">Share this code</span>

          <strong class="room-code-big">{{ roomCode }}</strong>

          <button
            type="button"
            class="copy-code-btn"
            :class="{ copied }"
            @click="copyCode"
          >
            {{ copied ? 'Copied!' : 'Copy code' }}
          </button>
        </div>

        <div v-else class="join-wrap">
          <input
            v-model="joinCode"
            class="room-join-input"
            type="text"
            placeholder="Enter 6-letter code..."
            maxlength="6"
            autocomplete="off"
            aria-label="Room code"
            @input="joinCode = joinCode.toUpperCase().replace(/[^A-Z0-9]/g, '')"
          />

          <span class="input-hint">
            {{ joinCode.length }}/6 characters
          </span>
        </div>
      </div>

      <button
        type="button"
        class="primary-action compact start-button"
        :disabled="!canStart"
        @click="start"
      >
        {{ buttonText }}
        <span class="arrow-icon">→</span>
      </button>
    </section>
  </div>
</template>

<style scoped>
.play-page {
  width: 100%;
  max-width: 1120px;
  margin: 0 auto;
  padding: 48px 24px 72px;
  box-sizing: border-box;
  color: var(--ink, #292d2c);
}

.center-heading {
  text-align: center;
  margin-bottom: 38px;
}

.section-kicker {
  color: var(--teal, #368d83);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 2.2px;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.page-title {
  font-family: var(--font-title, inherit);
  font-size: clamp(30px, 4vw, 42px);
  font-weight: 800;
  line-height: 1.15;
  margin: 0;
}

.page-subtitle {
  color: var(--muted, #777d79);
  font-size: 16px;
  line-height: 1.6;
  margin: 14px 0 0;
}

/* Game mode cards */

.mode-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.mode-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 0;
  min-height: 270px;
  padding: 26px;
  border: 2px solid transparent;
  border-radius: 22px;
  text-align: left;
  font: inherit;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.mode-card:hover {
  transform: translateY(-4px);
}

.mode-card:focus-visible {
  outline: 3px solid var(--teal, #368d83);
  outline-offset: 4px;
}

.mode-card.selected {
  border-color: currentColor;
  box-shadow: 0 8px 24px rgba(35, 45, 40, 0.09);
}

.mode-card.coral {
  background: #fff0eb;
  color: #c66c57;
}

.mode-card.teal {
  background: #e8f4ef;
  color: #368d83;
}

.mode-card.violet {
  background: #f1edfa;
  color: #8068b4;
}

.mode-check {
  position: absolute;
  top: 17px;
  right: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 25px;
  height: 25px;
  border-radius: 50%;
  background: currentColor;
  color: white;
  font-size: 14px;
  font-weight: 800;
}

.mode-illustration {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 65px;
  height: 65px;
  margin-bottom: 22px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.7);
  font-size: 35px;
}

.mode-title {
  color: #292d2c;
  font-size: 21px;
  font-weight: 800;
  margin-bottom: 7px;
}

.mode-subtitle {
  color: #555e59;
  font-size: 14px;
  font-weight: 600;
}

.mode-detail {
  color: #747c77;
  font-size: 13px;
  line-height: 1.5;
  margin-top: 13px;
}

.mode-note {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: auto;
  padding-top: 19px;
  font-size: 12px;
  font-weight: 700;
}

.spark-icon {
  font-size: 17px;
}

/* Game setup */

.game-setup {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 22px;
  margin-top: 28px;
  padding: 25px 28px;
  border: 1px solid var(--line, #e9e8e1);
  border-radius: 22px;
  background: var(--paper, #fffefa);
  box-shadow: 0 5px 20px rgba(35, 45, 40, 0.04);
}

.setup-copy {
  flex: 1 1 200px;
  min-width: 0;
}

.setup-title {
  margin: 0 0 7px;
  font-size: 19px;
  font-weight: 800;
}

.setup-sub {
  margin: 0;
  color: var(--muted, #777d79);
  font-size: 13px;
  line-height: 1.5;
}

/* Difficulty */

.difficulty {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  padding: 5px;
  border-radius: 12px;
  background: #f4f3ee;
}

.difficulty button,
.online-tabs-sm button {
  padding: 11px 13px;
  border: 0;
  border-radius: 9px;
  background: transparent;
  color: #656c67;
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease;
}

.difficulty button.chosen,
.online-tabs-sm button.chosen {
  background: white;
  color: var(--teal, #368d83);
  box-shadow: 0 2px 7px rgba(35, 45, 40, 0.08);
}

/* Online room */

.online-setup {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 190px;
}

.online-tabs-sm {
  display: flex;
  gap: 4px;
  padding: 4px;
  border-radius: 11px;
  background: #f4f3ee;
}

.online-tabs-sm button {
  flex: 1;
  white-space: nowrap;
}

.room-display {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.room-code-label {
  width: 100%;
  color: var(--muted, #777d79);
  font-size: 11px;
}

.room-code-big {
  color: #8068b4;
  font-size: 23px;
  letter-spacing: 4px;
}

.copy-code-btn {
  padding: 8px 12px;
  border: 1px solid #ded7ed;
  border-radius: 9px;
  background: white;
  color: #8068b4;
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.copy-code-btn.copied {
  background: #e8f4ef;
  border-color: #b8d9ce;
  color: #368d83;
}

.join-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.room-join-input {
  width: 100%;
  min-width: 190px;
  box-sizing: border-box;
  padding: 12px;
  border: 1px solid var(--line, #e9e8e1);
  border-radius: 10px;
  outline: none;
  background: white;
  color: #292d2c;
  font: inherit;
  font-size: 14px;
  letter-spacing: 2px;
}

.room-join-input:focus {
  border-color: var(--teal, #368d83);
}

.input-hint {
  color: var(--muted, #777d79);
  font-size: 11px;
}

/* Start button */

.primary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 13px;
  border: 0;
  border-radius: 13px;
  background: var(--coral, #d77961);
  color: white;
  font: inherit;
  font-weight: 800;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    opacity 0.2s ease;
}

.primary-action:hover:not(:disabled) {
  transform: translateY(-2px);
}

.primary-action:focus-visible {
  outline: 3px solid var(--teal, #368d83);
  outline-offset: 3px;
}

.primary-action:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.primary-action.compact {
  padding: 14px 19px;
  font-size: 14px;
}

.start-button {
  flex-shrink: 0;
  white-space: nowrap;
}

.arrow-icon {
  font-size: 19px;
}

/* Responsive layout */

@media (max-width: 850px) {
  .mode-grid {
    gap: 13px;
  }

  .mode-card {
    padding: 20px;
    min-height: 285px;
  }

  .game-setup {
    align-items: flex-start;
  }

  .setup-copy {
    flex-basis: 100%;
  }
}

@media (max-width: 650px) {
  .play-page {
    padding: 32px 16px 50px;
  }

  .center-heading {
    margin-bottom: 27px;
  }

  .page-subtitle {
    font-size: 14px;
  }

  .mode-grid {
    grid-template-columns: 1fr;
  }

  .mode-card {
    min-height: auto;
    padding: 19px;
  }

  .mode-illustration {
    width: 52px;
    height: 52px;
    margin-bottom: 13px;
    font-size: 29px;
  }

  .mode-title {
    font-size: 19px;
  }

  .mode-detail {
    margin-top: 8px;
  }

  .mode-note {
    padding-top: 12px;
  }

  .game-setup {
    flex-direction: column;
    padding: 20px;
  }

  .setup-copy,
  .difficulty,
  .online-setup,
  .start-button {
    width: 100%;
    box-sizing: border-box;
  }

  .difficulty {
    display: grid;
    grid-template-columns: 1fr;
  }

  .difficulty button {
    text-align: center;
  }

  .start-button {
    justify-content: center;
  }
}
</style>
