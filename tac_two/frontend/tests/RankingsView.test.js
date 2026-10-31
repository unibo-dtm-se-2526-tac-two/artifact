
import { describe, it, expect } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import { routes } from '../src/router'
import RankingsView from '../src/views/RankingsView.vue'

async function mountRankingsView() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes,
  })

  await router.push('/rankings')
  await router.isReady()

  const wrapper = mount(RankingsView, {
    global: {
      plugins: [router, createPinia()],
    },
  })

  await flushPromises()

  return wrapper
}

describe('RankingsView', () => {
  it('renders the rankings page heading', async () => {
    const wrapper = await mountRankingsView()

    expect(wrapper.find('h1').exists()).toBe(true)
  })

  it('displays ranking content', async () => {
    const wrapper = await mountRankingsView()

    expect(wrapper.text().toLowerCase()).toContain('ranking')
  })

  it('renders the rankings page without errors', async () => {
    const wrapper = await mountRankingsView()

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.rankings-page').exists()).toBe(true)
  })
})
