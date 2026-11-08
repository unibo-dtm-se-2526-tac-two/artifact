
import { describe, it, expect } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import GameView from '../src/views/GameView.vue'

async function mountGameView(path) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/play/local', component: GameView },
      { path: '/play/computer', component: GameView },
      { path: '/play/online', component: GameView },
      { path: '/play', component: { template: '<div>Play page</div>' } },
    ],
  })

  await router.push(path)
  await router.isReady()

  const wrapper = mount(GameView, {
    global: {
      plugins: [router],
    },
  })

  await flushPromises()

  return { wrapper, router }
}

describe('GameView', () => {
  it('shows Player 1 and Player 2 in local mode', async () => {
    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.text()).toContain('Player 1')
    expect(wrapper.text()).toContain('Player 2')
  })

  it('shows Mochi in computer mode', async () => {
    const { wrapper } = await mountGameView('/play/computer')

    expect(wrapper.text()).toContain('Mochi')
  })

  it('shows room information in online mode', async () => {
    const { wrapper } = await mountGameView(
      '/play/online?room=ABC123&opponent=Alex',
    )

    expect(wrapper.text()).toContain('ABC123')
    expect(wrapper.text()).toContain('Alex')
  })

  it('renders nine mini-boards', async () => {
    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.findAll('.mini-board')).toHaveLength(9)
  })

  it('renders 81 cells', async () => {
    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.findAll('.board-cell')).toHaveLength(81)
  })

  it('highlights the active mini-board', async () => {
    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.findAll('.active-board')).toHaveLength(1)
  })

  it('displays existing X and O marks', async () => {
    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.findAll('.mark-x').length).toBeGreaterThan(0)
    expect(wrapper.findAll('.mark-o').length).toBeGreaterThan(0)
  })

  it('opens settings when the settings button is clicked', async () => {
    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.find('.settings-modal').exists()).toBe(false)

    const settingsButton = wrapper.find('button[aria-label="Settings"]')

    await settingsButton.trigger('click')

    expect(wrapper.find('.settings-modal').exists()).toBe(true)
  })

  it('returns to Play when Leave game is clicked', async () => {
    const { wrapper, router } = await mountGameView('/play/local')

    const leaveButton = wrapper.findAll('button').find(button =>
      button.text().includes('Leave game'),
    )

    expect(leaveButton).toBeTruthy()

    await leaveButton.trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe('/play')
  })
})
