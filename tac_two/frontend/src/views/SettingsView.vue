
<script setup>
import { ref, watch } from 'vue'
import { settings, resetSettings } from '../settings.js'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close'])

const soundEffects = ref(true)

function closeModal() {
  emit('close')
}

function handleOverlayClick(event) {
  if (event.target === event.currentTarget) {
    closeModal()
  }
}

function resetAll() {
  resetSettings()
  soundEffects.value = true
}
</script>

<template>
  <div
    v-if="open"
    class="settings-overlay"
    @click="handleOverlayClick"
    @keydown.esc="closeModal"
  >
    <section class="settings-modal">
      <header class="settings-header">
        <div>
          <span class="settings-subtitle">GAME PREFERENCES</span>
          <h2>Settings</h2>
        </div>

        <button class="close-button" @click="closeModal">×</button>
      </header>

      <div class="settings-content">
        <!-- Player name -->
        <div class="setting-section">
          <h3>Player profile</h3>
          <label for="player-name">Display name</label>
          <input
            id="player-name"
            v-model="settings.playerName"
            type="text"
            maxlength="20"
            placeholder="Enter your name"
          />
        </div>

        <!-- Appearance -->
        <div class="setting-section">
          <h3>Appearance</h3>
          <label>Board marks</label>

          <div class="choice-group">
            <button
              :class="{ selected: settings.markStyle === 'classic' }"
              @click="settings.markStyle = 'classic'"
            >
              <span class="choice-symbol">× ○</span>
              Classic
            </button>

            <button
              :class="{ selected: settings.markStyle === 'cozy' }"
              @click="settings.markStyle = 'cozy'"
            >
              <span class="choice-symbol">🐾 🍃</span>
              Cozy
            </button>
          </div>

          <label class="checkbox-setting">
            <input
              v-model="settings.highlightBoards"
              type="checkbox"
            />
            Highlight available boards
          </label>
        </div>

        <!-- Audio -->
        <div class="setting-section">
          <h3>Audio</h3>
          <label class="checkbox-setting">
            <input v-model="soundEffects" type="checkbox" />
            Enable sound effects
          </label>
          <p class="setting-note">
            Sound effects can be connected when game audio is implemented.
          </p>
        </div>

        <!-- Gameplay -->
        <div class="setting-section">
          <h3>Gameplay</h3>

          <label for="difficulty">Default difficulty</label>
          <select id="difficulty" v-model="settings.difficulty">
            <option value="easy">Kitten Steps</option>
            <option value="medium">Clever Paws</option>
            <option value="hard">Tiger Mode</option>
          </select>

          <label for="clock">Default game timer</label>
          <select id="clock" v-model.number="settings.clockMinutes">
            <option :value="0">No timer</option>
            <option :value="3">3 minutes</option>
            <option :value="5">5 minutes</option>
            <option :value="10">10 minutes</option>
            <option :value="15">15 minutes</option>
          </select>

          <label class="checkbox-setting">
            <input v-model="settings.allowHints" type="checkbox" />
            Allow hints
          </label>
        </div>
      </div>

      <footer class="settings-footer">
        <button class="reset-button" @click="resetAll">
          Reset defaults
        </button>
        <button class="save-button" @click="closeModal">
          Save settings
        </button>
      </footer>
    </section>
  </div>
</template>

<style scoped>
.settings-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(25, 30, 35, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.settings-modal {
  width: 100%;
  max-width: 480px;
  max-height: 85vh;
  overflow-y: auto;
  background: var(--color-surface, #fff);
  color: var(--color-text, #292929);
  border-radius: 18px;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px 24px 16px;
  border-bottom: 1px solid #e8e8e8;
}

.settings-subtitle {
  font-size: 10px;
  letter-spacing: 1.5px;
  color: #999;
}

.settings-header h2 {
  margin: 5px 0 0;
  font-size: 24px;
}

.close-button {
  border: none;
  background: transparent;
  font-size: 28px;
  cursor: pointer;
  color: inherit;
}

.settings-content {
  padding: 8px 24px;
}

.setting-section {
  padding: 16px 0;
  border-bottom: 1px solid #eee;
}

.setting-section h3 {
  margin: 0 0 14px;
  font-size: 15px;
}

.setting-section > label:not(.checkbox-setting) {
  display: block;
  font-size: 13px;
  margin: 12px 0 7px;
  color: #777;
}

.setting-section input[type="text"],
.setting-section select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 9px;
  background: transparent;
  color: inherit;
  font: inherit;
  box-sizing: border-box;
}

.choice-group {
  display: flex;
  gap: 10px;
}

.choice-group button {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 10px;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.choice-group button.selected {
  border: 2px solid #8b9b75;
  background: #f2f5ed;
}

.choice-symbol {
  display: block;
  font-size: 20px;
  margin-bottom: 5px;
}

.checkbox-setting {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 14px;
  font-size: 13px;
  cursor: pointer;
}

.checkbox-setting input {
  accent-color: #82956b;
}

.setting-note {
  color: #999;
  font-size: 11px;
  line-height: 1.5;
}

.settings-footer {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 16px 24px 22px;
}

.settings-footer button {
  padding: 10px 16px;
  border-radius: 9px;
  font-size: 13px;
  cursor: pointer;
}

.reset-button {
  border: 1px solid #ddd;
  background: transparent;
  color: inherit;
}

.save-button {
  border: none;
  background: #82956b;
  color: white;
}

@media (max-width: 500px) {
  .settings-overlay {
    padding: 10px;
  }

  .settings-modal {
    max-height: 90vh;
  }

  .settings-content {
    padding: 8px 18px;
  }

  .settings-header,
  .settings-footer {
    padding-left: 18px;
    padding-right: 18px;
  }
}
</style>
