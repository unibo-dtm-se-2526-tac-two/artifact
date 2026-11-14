import { describe, it, expect } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import PlayView from '../src/views/PlayView.vue'
import { settings } from '../src/settings.js'

async function mountPlayView() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/play', component: PlayView },
      { path: '/play/local', component: { template: '<div>Local game</div>' } },
      { path: '/play/computer', component: { template: '<div>Computer game</div>' } },
      { path: '/play/online', component: { template: '<div>Online game</div>' } },
    ],
  })

  await router.push('/play')
  await router.isReady()

  const wrapper = mount(PlayView, {
    global: {
      plugins: [router],
    },
  })

  await flushPromises()

  return { wrapper, router }
}

describe('PlayView', () => {
  it('shows the three game modes', async () => {
    const { wrapper } = await mountPlayView()

    expect(wrapper.text()).toContain('Pass & play')
    expect(wrapper.text()).toContain('Challenge Mochi')
    expect(wrapper.text()).toContain('Online room')
  })

  it('shows all three difficulty levels', async () => {
    const { wrapper } = await mountPlayView()

    expect(wrapper.text()).toContain('Kitten Steps')
    expect(wrapper.text()).toContain('Clever Paws')
    expect(wrapper.text()).toContain('Tiger Mode')
  })

  it('lets the player choose a game clock before starting', async () => {
    const { wrapper } = await mountPlayView()

    const clock = wrapper.find('#play-clock')
    expect(clock.exists()).toBe(true)

    await clock.setValue('0')

    expect(clock.element.value).toBe('0')
    expect(settings.clockMinutes).toBe(0)
    settings.clockMinutes = 5
  })

  it('selects a game mode when clicked', async () => {
    const { wrapper } = await mountPlayView()

    const localMode = wrapper.findAll('.mode-card')[0]

    await localMode.trigger('click')

    expect(localMode.classes()).toContain('selected')
    expect(localMode.attributes('aria-pressed')).toBe('true')
  })

  it('starts a local game', async () => {
    const { wrapper, router } = await mountPlayView()

    await wrapper.findAll('.mode-card')[0].trigger('click')
    await wrapper.find('.start-button').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe('/play/local')
  })

  it('starts a computer game with the selected difficulty', async () => {
    const { wrapper, router } = await mountPlayView()

    const hardLevel = wrapper.findAll('.difficulty button')[2]
    await hardLevel.trigger('click')

    await wrapper.find('.start-button').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe('/play/computer')
    expect(router.currentRoute.value.query.level).toBe('hard')
  })

  it('allows the player to enter a room code', async () => {
    const { wrapper } = await mountPlayView()

    await wrapper.findAll('.mode-card')[2].trigger('click')
    await wrapper.find('.online-tabs-sm button:nth-child(2)').trigger('click')

    const input = wrapper.find('.room-join-input')

    await input.setValue('abc123')

    expect(input.element.value).toBe('ABC123')
    expect(wrapper.text()).toContain('6/6 characters')
  })

  it('disables Join room when the code is incomplete', async () => {
    const { wrapper } = await mountPlayView()

    await wrapper.findAll('.mode-card')[2].trigger('click')
    await wrapper.find('.online-tabs-sm button:nth-child(2)').trigger('click')

    expect(wrapper.find('.start-button').attributes('disabled')).toBeDefined()
  })

  it('joins an online room with the entered code', async () => {
    const { wrapper, router } = await mountPlayView()

    await wrapper.findAll('.mode-card')[2].trigger('click')
    await wrapper.find('.online-tabs-sm button:nth-child(2)').trigger('click')
    await wrapper.find('.room-join-input').setValue('abc123')

    await wrapper.find('.start-button').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe('/play/online')
    expect(router.currentRoute.value.query.room).toBe('ABC123')
  })
})