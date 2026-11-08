
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

  it('updates the player name', async () => {
    const wrapper = mountSettingsView()

    await wrapper.find('#player-name').setValue('Alex')

    expect(settings.playerName).toBe('Alex')
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

  it('updates the difficulty', async () => {
    const wrapper = mountSettingsView()

    await wrapper.find('#difficulty').setValue('hard')

    expect(settings.difficulty).toBe('hard')
  })

  it('updates the game timer', async () => {
    const wrapper = mountSettingsView()

    await wrapper.find('#clock').setValue('10')

    expect(settings.clockMinutes).toBe(10)
  })

  it('updates the highlight boards setting', async () => {
    const wrapper = mountSettingsView()

    await wrapper.find('input[type="checkbox"]').setValue(false)

    expect(settings.highlightBoards).toBe(false)
  })

  it('updates the hints setting', async () => {
    const wrapper = mountSettingsView()

    const checkboxes = wrapper.findAll('input[type="checkbox"]')

    await checkboxes[2].setValue(false)

    expect(settings.allowHints).toBe(false)
  })

  it('resets settings to their default values', async () => {
    const wrapper = mountSettingsView()

    settings.playerName = 'Alex'
    settings.markStyle = 'cozy'
    settings.clockMinutes = 10
    settings.difficulty = 'hard'
    settings.highlightBoards = false
    settings.allowHints = false

    await wrapper.find('.reset-button').trigger('click')

    expect(settings.playerName).toBe('Player')
    expect(settings.markStyle).toBe('classic')
    expect(settings.clockMinutes).toBe(5)
    expect(settings.difficulty).toBe('medium')
    expect(settings.highlightBoards).toBe(true)
    expect(settings.allowHints).toBe(true)
  })
})
