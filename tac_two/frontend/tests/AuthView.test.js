
import { describe, it, expect } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import { routes } from '../src/router'
import AuthView from '../src/views/AuthView.vue'

async function mountAuthView() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes,
  })

  await router.push('/login')
  await router.isReady()

  const wrapper = mount(AuthView, {
    global: {
      plugins: [router, createPinia()],
    },
  })

  await flushPromises()

  return wrapper
}

describe('AuthView', () => {
  it('renders the authentication page', async () => {
    const wrapper = await mountAuthView()

    expect(wrapper.exists()).toBe(true)
  })

  it('displays a heading', async () => {
    const wrapper = await mountAuthView()

    expect(wrapper.find('h1').exists()).toBe(true)
  })

  it('contains a form', async () => {
    const wrapper = await mountAuthView()

    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('contains input fields', async () => {
    const wrapper = await mountAuthView()

    expect(wrapper.findAll('input').length).toBeGreaterThan(0)
  })
})
