
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RankingsView from '../src/views/RankingsView.vue'

describe('RankingsView', () => {
  it('renders the rankings page', () => {
    const wrapper = mount(RankingsView)

    expect(wrapper.find('.leaderboard-page').exists()).toBe(true)
  })

  it('displays the leaderboard heading', () => {
    const wrapper = mount(RankingsView)

    expect(wrapper.text()).toContain('The leaf board')
    expect(wrapper.text()).toContain('Hall of clever moves')
  })

  it('displays the season information', () => {
    const wrapper = mount(RankingsView)

    expect(wrapper.text()).toContain('Spring season')
    expect(wrapper.text()).toContain('12 days left')
  })

  it('displays six players in the ranking table', () => {
    const wrapper = mount(RankingsView)

    expect(wrapper.findAll('.ranking-row')).toHaveLength(6)
  })

  it('displays the podium with three players', () => {
    const wrapper = mount(RankingsView)

    expect(wrapper.findAll('.podium-player')).toHaveLength(3)
  })

  it('displays the current user', () => {
    const wrapper = mount(RankingsView)

    expect(wrapper.text()).toContain('Sofia')
    expect(wrapper.text()).toContain('You')
  })

  it('sorts players by leaves', () => {
    const wrapper = mount(RankingsView)
    const rows = wrapper.findAll('.ranking-row')

    expect(rows[0].text()).toContain('LunaLoops')
    expect(rows[1].text()).toContain('GridWizard')
    expect(rows[2].text()).toContain('TeaAndTactics')
  })
})
