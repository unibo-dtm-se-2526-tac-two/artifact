// Settings shared by the Settings page, the Play page and the Game page.
// They are saved in the browser (localStorage), so they stay after a refresh.
import { reactive, watch } from 'vue'

const KEY = 'tac2-settings'

const defaults = {
  playerName: 'Player',
  markStyle: 'classic', // 'classic' (× ○) or 'cozy' (paw and leaf)
  clockMinutes: 5, // 0 = no clock
  difficulty: 'medium', // 'easy' | 'medium' | 'hard'
  highlightBoards: true, // glow on the boards you are allowed to play in
  allowHints: true, // show the Hint button
}

function load() {
  try {
    return { ...defaults, ...JSON.parse(localStorage.getItem(KEY)) }
  } catch {
    return { ...defaults }
  }
}

export const settings = reactive(load())

// Save every time something changes
watch(settings, () => localStorage.setItem(KEY, JSON.stringify(settings)), { deep: true })

export function resetSettings() {
  Object.assign(settings, defaults)
}