import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '../src/stores/auth'
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
  // every answer is a fresh copy, like a real server (the page changes the game it gets)
  const fetchMock = vi.fn(async () => ({
    ok: true,
    json: async () => structuredClone(reply),
  }))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

async function mountGameView(path, pinia = createPinia()) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/play/local', component: GameView },
      { path: '/play/computer', component: GameView },
      { path: '/play/online', component: GameView },
      { path: '/play', component: { template: '<div>Play page</div>' } },
      { path: '/login', name: 'login', component: { template: '<div>Login page</div>' } },
    ],
  })

  await router.push(path)
  await router.isReady()

  // Like in the real app the page is shown by a RouterView: only then the
  // "do you want to leave?" guard of the page is active.
  const wrapper = mount(
    { template: '<RouterView />' },
    { global: { plugins: [router, pinia] } },
  )

  await flushPromises()

  return { wrapper, router }
}

// The game (and its clock) is created with the FIRST MOVE, so most tests start
// by clicking one cell.
async function playFirstMove(wrapper, index = 0) {
  await wrapper.findAll('.board-cell')[index].trigger('click')
  await flushPromises()
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

  it('does not create a game (and does not start the clock) when the page opens', async () => {
    const fetchMock = mockApi(fakeGame())
    const { wrapper } = await mountGameView('/play/local')

    expect(fetchMock).not.toHaveBeenCalled()
    expect(wrapper.findAll('.board-cell:not(:disabled)')).toHaveLength(81)
  })

  it('asks the backend to start a local game with the first move', async () => {
    const fetchMock = mockApi(fakeGame())
    const { wrapper } = await mountGameView('/play/local')

    await playFirstMove(wrapper)

    // first the game is created, then the move is played
    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/v1/games')
    expect(options.method).toBe('POST')
    expect(JSON.parse(options.body).mode).toBe('local')
    expect(fetchMock.mock.calls[1][0]).toBe('/api/v1/games/game-1/moves')
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({ board: 0, cell: 0 })
  })

  it('keeps the clock still before the first move', async () => {
    vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval', 'Date'] })
    try {
      const { wrapper } = await mountGameView('/play/local')
      await vi.advanceTimersByTimeAsync(5000)

      const times = wrapper.findAll('.timer strong').map((t) => t.text())
      expect(times).toEqual(['05:00', '05:00'])
    } finally {
      vi.useRealTimers()
    }
  })

  it('sends the selected clock setting to the backend', async () => {
    settings.clockMinutes = 3
    const fetchMock = mockApi(fakeGame({ clock: { x: 180, o: 180, active: 'X' } }))

    const { wrapper } = await mountGameView('/play/local')
    await playFirstMove(wrapper)

    const body = JSON.parse(fetchMock.mock.calls[0][1].body)
    expect(body.minutes).toBe(3)
  })

  it('asks the backend for the chosen difficulty in computer mode', async () => {
    const fetchMock = mockApi(
      fakeGame({ mode: 'computer', difficulty: 'hard', human_player: 'X' }),
    )
    const { wrapper } = await mountGameView('/play/computer?level=hard')
    await playFirstMove(wrapper)

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
    await playFirstMove(wrapper)

    expect(wrapper.findAll('.active-board')).toHaveLength(1)
  })

  it('displays the X and O marks sent by the backend', async () => {
    const boards = Array.from({ length: 9 }, () => Array(9).fill(null))
    boards[4][4] = 'X'
    boards[4][0] = 'O'
    mockApi(fakeGame({ boards, move_count: 2 }))

    const { wrapper } = await mountGameView('/play/local')
    await playFirstMove(wrapper)

    expect(wrapper.findAll('.mark-x')).toHaveLength(1)
    expect(wrapper.findAll('.mark-o')).toHaveLength(1)
  })

  it('sends the move to the backend when a cell is clicked', async () => {
    const afterMove = fakeGame({ current_player: 'O', forced_board: 0 })
    afterMove.boards[0][0] = 'X'

    const fetchMock = mockApi(fakeGame())
    const { wrapper } = await mountGameView('/play/local')

    // the creation of the game gets an empty game, the move gets the new situation
    fetchMock.mockImplementation(async (url) => ({
      ok: true,
      json: async () => (url.endsWith('/moves') ? afterMove : fakeGame()),
    }))

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
    await playFirstMove(wrapper, 9) // a cell of the second board

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
    await playFirstMove(wrapper)

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
    await playFirstMove(wrapper)

    expect(wrapper.find('.game-banner.result').text()).toContain('wins')
    expect(wrapper.text()).toContain('Play again')
  })

  it('shows an error when the backend is not reachable', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => { throw new Error('offline') }))
    const { wrapper } = await mountGameView('/play/local')
    await playFirstMove(wrapper)

    expect(wrapper.find('.game-banner.error').exists()).toBe(true)
    // nothing was played: the board stays empty and can be tried again
    expect(wrapper.findAll('.mark-x')).toHaveLength(0)
    expect(wrapper.findAll('.board-cell:not(:disabled)')).toHaveLength(81)
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

  /* ---------- the game is lost (backend restarted) or the sign-in ended ---------- */

  // The backend answers the creation of the game, but refuses every move
  function mockApiWithMoveError(status, detail) {
    const fetchMock = vi.fn(async (url, options = {}) => {
      if (options.method === 'POST' && url.endsWith('/moves')) {
        return { ok: false, status, json: async () => ({ detail }) }
      }
      return { ok: true, status: 200, json: async () => fakeGame() }
    })
    vi.stubGlobal('fetch', fetchMock)
    return fetchMock
  }

  it('takes the mark back and blocks the board when the backend lost the game', async () => {
    mockApiWithMoveError(404, 'Game not found.')
    const { wrapper } = await mountGameView('/play/local')

    await wrapper.findAll('.board-cell')[0].trigger('click')
    await flushPromises()

    // no ghost move on the board, and the player is told what happened
    expect(wrapper.findAll('.mark-x')).toHaveLength(0)
    expect(wrapper.find('.problem-dialog').exists()).toBe(true)
    expect(wrapper.find('.problem-dialog').text()).toContain('no longer available')

    // the board cannot be used any more: no endless moves
    expect(wrapper.findAll('.board-cell:not(:disabled)')).toHaveLength(0)
  })

  it('offers a new game when the backend lost the game', async () => {
    const fetchMock = mockApiWithMoveError(404, 'Game not found.')
    const { wrapper } = await mountGameView('/play/local')

    await wrapper.findAll('.board-cell')[0].trigger('click')
    await flushPromises()

    const newGame = wrapper.findAll('.problem-dialog button').find((b) => b.text() === 'New game')
    await newGame.trigger('click')
    await flushPromises()

    expect(wrapper.find('.problem-dialog').exists()).toBe(false)
    // a fresh, empty board: the new game is created with its first move
    expect(wrapper.findAll('.mark-x')).toHaveLength(0)
    expect(wrapper.findAll('.board-cell:not(:disabled)')).toHaveLength(81)
  })

  it('asks to sign in again when the sign-in has ended', async () => {
    mockApiWithMoveError(403, 'This game belongs to another player.')
    const { wrapper, router } = await mountGameView('/play/local')

    await wrapper.findAll('.board-cell')[0].trigger('click')
    await flushPromises()

    expect(wrapper.find('.problem-dialog').text()).toContain('sign-in has ended')

    const signIn = wrapper.findAll('.problem-dialog button').find((b) => b.text() === 'Sign in again')
    await signIn.trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/play/local')
  })

  it('shows a normal error (not a popup) when the server cannot be reached', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => { throw new TypeError('Failed to fetch') }))
    const { wrapper } = await mountGameView('/play/local')
    await playFirstMove(wrapper)

    expect(wrapper.find('.game-banner.error').text()).toContain('Cannot reach the game server')
    expect(wrapper.find('.problem-dialog').exists()).toBe(false)
  })

  /* ---------- popup when the player quits ---------- */

  function leaveButton(wrapper) {
    return wrapper.findAll('button').find((button) => button.text().includes('Leave game'))
  }

  it('asks before leaving a game in progress', async () => {
    mockApi(fakeGame({ move_count: 4 }))
    const { wrapper, router } = await mountGameView('/play/local')
    await playFirstMove(wrapper)

    await leaveButton(wrapper).trigger('click')
    await flushPromises()

    expect(wrapper.find('.leave-dialog').exists()).toBe(true)
    expect(wrapper.find('.leave-dialog').text()).toContain('progress in this game will be lost')
    expect(router.currentRoute.value.path).toBe('/play/local') // still here
  })

  it('stays in the game when the player chooses to keep playing', async () => {
    mockApi(fakeGame({ move_count: 4 }))
    const { wrapper, router } = await mountGameView('/play/local')
    await playFirstMove(wrapper)

    await leaveButton(wrapper).trigger('click')
    await flushPromises()
    await wrapper.find('.leave-dialog .dialog-button.primary').trigger('click')
    await flushPromises()

    expect(wrapper.find('.leave-dialog').exists()).toBe(false)
    expect(router.currentRoute.value.path).toBe('/play/local')
  })

  it('leaves the game after the player confirms', async () => {
    mockApi(fakeGame({ move_count: 4 }))
    const { wrapper, router } = await mountGameView('/play/local')
    await playFirstMove(wrapper)

    await leaveButton(wrapper).trigger('click')
    await flushPromises()
    await wrapper.find('.leave-dialog .dialog-button.danger').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe('/play')
  })

  it('leaves without a question when nobody has played yet', async () => {
    const fetchMock = mockApi(fakeGame({ move_count: 0 }))
    const { wrapper, router } = await mountGameView('/play/local')

    await leaveButton(wrapper).trigger('click')
    await flushPromises()

    expect(wrapper.find('.leave-dialog').exists()).toBe(false)
    expect(router.currentRoute.value.path).toBe('/play')
    expect(fetchMock).not.toHaveBeenCalled() // no game was ever created
  })

  it('leaves without a question when the game is over', async () => {
    mockApi(
      fakeGame({ status: 'finished', current_player: null, winner: 'X', end_reason: 'win', move_count: 30 }),
    )
    const { wrapper, router } = await mountGameView('/play/local')
    await playFirstMove(wrapper)

    await leaveButton(wrapper).trigger('click')
    await flushPromises()

    expect(wrapper.find('.leave-dialog').exists()).toBe(false)
    expect(router.currentRoute.value.path).toBe('/play')
  })

  it('asks before leaving through the browser back button too', async () => {
    mockApi(fakeGame({ move_count: 4 }))
    const { wrapper, router } = await mountGameView('/play/local')
    await playFirstMove(wrapper)

    router.push('/play') // the same thing the menu or the back button does
    await flushPromises()

    expect(wrapper.find('.leave-dialog').exists()).toBe(true)
    expect(router.currentRoute.value.path).toBe('/play/local')
  })

  /* ---------- the clock ---------- */

  it('counts down the clock of the player on turn only', async () => {
    vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval', 'Date'] })
    try {
      const { wrapper } = await mountGameView('/play/local')
      await playFirstMove(wrapper) // the clock starts with the first move

      await vi.advanceTimersByTimeAsync(3000)

      const times = wrapper.findAll('.timer strong').map((t) => t.text())
      expect(times[0]).toBe('04:57') // X is on turn
      expect(times[1]).toBe('05:00') // O waits
    } finally {
      vi.useRealTimers()
    }
  })

  /* ---------- the player and the leaves come from the account and the database ---------- */

  it('shows the username of the signed-in player', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const authStore = useAuthStore()
    authStore.user = { username: 'sofia_sc' }
    authStore.isAuthenticated = true

    const { wrapper } = await mountGameView('/play/local', pinia)

    expect(wrapper.find('.player-one').text()).toContain('sofia_sc')
  })

  it('shows the leaves earned when a game against Mochi ends', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const authStore = useAuthStore()
    authStore.token = 'token'
    authStore.isAuthenticated = true
    authStore.profile = { leaves: 10, level: { number: 1 } }

    const playing = fakeGame({ mode: 'computer', difficulty: 'medium', human_player: 'X' })
    const finished = fakeGame({
      mode: 'computer',
      difficulty: 'medium',
      human_player: 'X',
      status: 'finished',
      current_player: null,
      winner: 'X',
      end_reason: 'win',
      move_count: 21,
    })

    vi.stubGlobal(
      'fetch',
      vi.fn(async (url, options = {}) => {
        const reply = url.endsWith('/moves')
          ? finished
          : url.endsWith('/users/me/stats')
            ? { overall: { played: 2, wins: 1, losses: 0, draws: 0, win_rate: 1 }, best_streak: 1, by_difficulty: { medium: { wins: 1, draws: 0, losses: 0 }, easy: { wins: 1, draws: 0, losses: 0 } } }
            : playing
        return { ok: true, status: 200, json: async () => reply }
      }),
    )

    const { wrapper } = await mountGameView('/play/computer', pinia)

    await wrapper.findAll('.board-cell')[0].trigger('click')
    await flushPromises()

    expect(wrapper.find('.game-banner.result').text()).toContain('+25')
    expect(authStore.profile.leaves).toBe(35)
  })
})