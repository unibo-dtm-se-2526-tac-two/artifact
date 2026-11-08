import { describe, it, expect } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import { routes } from '../src/router'
import App from '../src/App.vue'

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes,
  })
}

async function mountApp() {
  const router = createTestRouter()
  await router.push('/')
  await router.isReady()

  const wrapper = mount(App, {
    global: {
      plugins: [router, createPinia()],
    },
  })

  await flushPromises()

  return { wrapper, router }
}

describe('App', () => {
  it('shows the four tabs', async () => {
    const { wrapper } = await mountApp()

    expect(wrapper.findAll('.tab')).toHaveLength(4)

    expect(wrapper.text()).toContain('Home')
    expect(wrapper.text()).toContain('Play')
    expect(wrapper.text()).toContain('Learn')
    expect(wrapper.text()).toContain('Rankings')
  })

  it('starts with the Home tab active', async () => {
    const { wrapper } = await mountApp()

    expect(wrapper.find('.tab.active').text()).toContain('Home')
  })

  it('shows the sign-in button when the user is not authenticated', async () => {
    const { wrapper } = await mountApp()

    expect(wrapper.find('.signin').exists()).toBe(true)
  })
})