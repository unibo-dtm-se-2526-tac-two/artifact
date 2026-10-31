
import { describe, it, expect } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import PlayView from '../src/views/PlayView.vue'

async function mountPlayView() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/play', component: PlayView },
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

  return wrapper
}

describe('PlayView', () => {
  it('shows the three game modes', async () => {
    const wrapper = await mountPlayView()

    expect(wrapper.text()).toContain('Local match')
    expect(wrapper.text()).toContain('Play vs Mochi')
    expect(wrapper.text()).toContain('Online room')
  })

  it('shows all three difficulty levels', async () => {
    const wrapper = await mountPlayView()

    expect(wrapper.text()).toContain('Cozy')
    expect(wrapper.text()).toContain('Tricky')
    expect(wrapper.text()).toContain('Mastermind')
  })

  it('links to the correct game modes', async () => {
    const wrapper = await mountPlayView()

    expect(wrapper.find('a[href="/play/local"]').exists()).toBe(true)
    expect(wrapper.find('a[href="/play/computer?level=easy"]').exists()).toBe(true)
    expect(wrapper.find('a[href="/play/online"]').exists()).toBe(true)
  })

  it('highlights the preferred difficulty', async () => {
    const wrapper = await mountPlayView()

    expect(wrapper.find('.level-chip.preferred').exists()).toBe(true)
  })

  it('displays the clock information', async () => {
    const wrapper = await mountPlayView()

    expect(wrapper.text()).toContain('Clock:')
  })
})
