import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import GameView from '../src/views/GameView.vue'
import { settings } from '../src/settings.js'

// A game as the Python backend sends it
function fakeGame(changes = {}) {
  return {
    id: 'game-1',
    mode: 'local',
    difficulty: null,
    human_player: null,
    status: 'playing',
    current_player: 'X',
    forced_board: null,
    boards: Array.from({ length: 9 }, () => Array(9).fill(null)),
    board_winners: Array(9).fill(null),
    winner: null,
    end_reason: null,
    clock: { x: 300, o: 300, active: 'X' },
    move_count: 0,
    last_moves: [],
    ...changes,
  }
}

// Replace fetch with a fake: it answers every request with `reply`
function mockApi(reply) {
  const fetchMock = vi.fn(async () => ({
    ok: true,
    json: async () => reply,
  }))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

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
    global: { plugins: [router, createPinia()] },
  })

  await flushPromises()

  return { wrapper, router }
}

describe('GameView', () => {
  beforeEach(() => {
    mockApi(fakeGame())
  })

  afterEach(() => {
    settings.clockMinutes = 5
    settings.difficulty = 'medium'
    vi.unstubAllGlobals()
  })

  it('shows Player 1 and Player 2 in local mode', async () => {
    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.text()).toContain('Player 1')
    expect(wrapper.text()).toContain('Player 2')
  })

  it('shows Mochi in computer mode', async () => {
    mockApi(fakeGame({ mode: 'computer', difficulty: 'medium', human_player: 'X' }))
    const { wrapper } = await mountGameView('/play/computer')

    expect(wrapper.text()).toContain('Mochi')
  })

  it('shows room information in online mode', async () => {
    const { wrapper } = await mountGameView('/play/online?room=ABC123&opponent=Alex')

    expect(wrapper.text()).toContain('ABC123')
    expect(wrapper.text()).toContain('Alex')
  })

  it('asks the backend to start a local game', async () => {
    const fetchMock = mockApi(fakeGame())
    await mountGameView('/play/local')

    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/v1/games')
    expect(options.method).toBe('POST')
    expect(JSON.parse(options.body).mode).toBe('local')
  })

  it('sends the selected clock setting to the backend', async () => {
    settings.clockMinutes = 3
    const fetchMock = mockApi(fakeGame({ clock: { x: 180, o: 180, active: 'X' } }))

    await mountGameView('/play/local')

    const body = JSON.parse(fetchMock.mock.calls[0][1].body)
    expect(body.minutes).toBe(3)
  })

  it('asks the backend for the chosen difficulty in computer mode', async () => {
    const fetchMock = mockApi(
      fakeGame({ mode: 'computer', difficulty: 'hard', human_player: 'X' }),
    )
    await mountGameView('/play/computer?level=hard')

    const body = JSON.parse(fetchMock.mock.calls[0][1].body)
    expect(body.mode).toBe('computer')
    expect(body.difficulty).toBe('hard')
  })

  it('does not call the backend in online mode (not ready yet)', async () => {
    const fetchMock = mockApi(fakeGame())
    await mountGameView('/play/online?room=ABC123')

    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('renders nine mini-boards and 81 cells', async () => {
    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.findAll('.mini-board')).toHaveLength(9)
    expect(wrapper.findAll('.board-cell')).toHaveLength(81)
  })

  it('highlights only the board where the player must play', async () => {
    mockApi(fakeGame({ forced_board: 3 }))
    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.findAll('.active-board')).toHaveLength(1)
  })

  it('displays the X and O marks sent by the backend', async () => {
    const boards = Array.from({ length: 9 }, () => Array(9).fill(null))
    boards[4][4] = 'X'
    boards[4][0] = 'O'
    mockApi(fakeGame({ boards, move_count: 2 }))

    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.findAll('.mark-x')).toHaveLength(1)
    expect(wrapper.findAll('.mark-o')).toHaveLength(1)
  })

  it('sends the move to the backend when a cell is clicked', async () => {
    const afterMove = fakeGame({ current_player: 'O', forced_board: 0 })
    afterMove.boards[0][0] = 'X'

    const fetchMock = mockApi(fakeGame())
    const { wrapper } = await mountGameView('/play/local')

    fetchMock.mockImplementation(async () => ({ ok: true, json: async () => afterMove }))

    await wrapper.findAll('.board-cell')[0].trigger('click')
    await flushPromises()

    const [url, options] = fetchMock.mock.calls.at(-1)
    expect(url).toBe('/api/v1/games/game-1/moves')
    expect(JSON.parse(options.body)).toEqual({ board: 0, cell: 0 })
    expect(wrapper.findAll('.mark-x')).toHaveLength(1)
  })

  it('does not let you play inside a finished board', async () => {
    const winners = Array(9).fill(null)
    winners[0] = 'X'
    mockApi(fakeGame({ board_winners: winners }))

    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.findAll('.board-cell')[0].attributes('disabled')).toBeDefined()
    expect(wrapper.findAll('.board-result')).toHaveLength(1)
  })

  it('blocks the cells while the computer is thinking', async () => {
    mockApi(
      fakeGame({
        mode: 'computer',
        difficulty: 'easy',
        human_player: 'X',
        current_player: 'O',
      }),
    )
    const { wrapper } = await mountGameView('/play/computer')

    expect(wrapper.findAll('.board-cell:not(:disabled)')).toHaveLength(0)
  })

  it('shows the result when the game is over', async () => {
    mockApi(
      fakeGame({
        status: 'finished',
        current_player: null,
        winner: 'X',
        end_reason: 'win',
      }),
    )
    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.find('.game-banner.result').text()).toContain('wins')
    expect(wrapper.text()).toContain('Play again')
  })

  it('shows an error when the backend is not reachable', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => { throw new Error('offline') }))
    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.find('.game-banner.error').exists()).toBe(true)
  })

  it('opens settings when the settings button is clicked', async () => {
    const { wrapper } = await mountGameView('/play/local')

    expect(wrapper.find('.settings-modal').exists()).toBe(false)

    await wrapper.find('button[aria-label="Settings"]').trigger('click')

    expect(wrapper.find('.settings-modal').exists()).toBe(true)
  })

  it('returns to Play when Leave game is clicked', async () => {
    const { wrapper, router } = await mountGameView('/play/local')

    const leaveButton = wrapper
      .findAll('button')
      .find((button) => button.text().includes('Leave game'))

    expect(leaveButton).toBeTruthy()

    await leaveButton.trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe('/play')
  })
})