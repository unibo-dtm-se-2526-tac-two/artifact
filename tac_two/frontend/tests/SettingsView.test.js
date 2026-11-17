import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import SettingsView from '../src/views/SettingsView.vue'
import { settings, resetSettings } from '../src/settings.js'

function mountSettingsView(open = true) {
  return mount(SettingsView, {
    props: { open },
  })
}

describe('SettingsView', () => {
  beforeEach(() => {
    resetSettings()
    localStorage.clear()
  })

  it('shows the settings modal when open is true', () => {
    const wrapper = mountSettingsView(true)

    expect(wrapper.find('.settings-modal').exists()).toBe(true)
    expect(wrapper.text()).toContain('Settings')
  })

  it('does not show the modal when open is false', () => {
    const wrapper = mountSettingsView(false)

    expect(wrapper.find('.settings-modal').exists()).toBe(false)
  })

  it('emits close when the close button is clicked', async () => {
    const wrapper = mountSettingsView()

    await wrapper.find('.close-button').trigger('click')

    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('emits close when Save settings is clicked', async () => {
    const wrapper = mountSettingsView()

    await wrapper.find('.save-button').trigger('click')

    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('changes the board marks to Cozy', async () => {
    const wrapper = mountSettingsView()

    await wrapper.findAll('.choice-group button')[1].trigger('click')

    expect(settings.markStyle).toBe('cozy')
  })

  it('changes the board marks to Classic', async () => {
    const wrapper = mountSettingsView()

    settings.markStyle = 'cozy'

    await wrapper.findAll('.choice-group button')[0].trigger('click')

    expect(settings.markStyle).toBe('classic')
  })

  it('updates the highlight boards setting', async () => {
    const wrapper = mountSettingsView()

    await wrapper.findAll('input[type="checkbox"]')[0].setValue(false)

    expect(settings.highlightBoards).toBe(false)
  })

  it('saves the sound effects setting', async () => {
    const wrapper = mountSettingsView()

    await wrapper.findAll('input[type="checkbox"]')[1].setValue(false)

    expect(settings.soundEffects).toBe(false)
  })

  it('does not offer the difficulty or the timer (they are chosen on the Play page)', () => {
    const wrapper = mountSettingsView()

    expect(wrapper.find('#difficulty').exists()).toBe(false)
    expect(wrapper.find('#clock').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('Gameplay')
  })

  it('resets settings to their default values', async () => {
    const wrapper = mountSettingsView()

    settings.markStyle = 'cozy'
    settings.highlightBoards = false
    settings.soundEffects = false

    await wrapper.find('.reset-button').trigger('click')

    expect(settings.markStyle).toBe('classic')
    expect(settings.highlightBoards).toBe(true)
    expect(settings.soundEffects).toBe(true)
  })
})