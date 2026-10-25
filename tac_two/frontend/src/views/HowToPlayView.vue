<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const badges = ['✦ Easy to learn', '♟ Two players', '♡ Strategy first']

// Each mini board has 9 squares ('' = empty)
const steps = [
  {
    color: 'coral',
    number: '01',
    title: 'Take your turn',
    text: 'Players take turns placing their mark, X or O, in an empty square.',
    board: ['×', '', '○', '', '×', '', '○', '', ''],
  },
  {
    color: 'teal',
    number: '02',
    title: 'Think one move ahead',
    text: 'Your move determines which small board your opponent must play in next.',
    board: ['', '×', '', '', '○', '', '', '×', ''],
  },
  {
    color: 'violet',
    number: '03',
    title: 'Win the big board',
    text: 'Win small boards by making three in a row. Win the overall game by claiming three small boards in a row.',
    board: ['×', '×', '×', '○', '○', '', '', '', ''],
  },
]

// Example big board: 9 small boards.
// "marks" = { squareNumber: symbol }, squares are numbered 0-8 (4 is the centre).
const exampleBoards = [
  { marks: { 4: '×' } },
  { marks: { 4: '○' } },
  { marks: { 1: '×' } },
  { marks: {} },
  { marks: { 4: '○' } },
  { marks: { 4: '×' }, target: true },
  { marks: {} },
  { marks: {} },
  { marks: {} },
]

const tips = [
  { icon: '✦', title: 'Plan ahead', text: "Think about your next move and your opponent's options." },
  { icon: '♡', title: 'Watch the whole board', text: 'A small-board win can bring you closer to the big one.' },
  { icon: '☁', title: 'Enjoy the game', text: 'Every round is a chance to learn a new strategy.' },
]
</script>

<template>
  <section class="how-to-play-page">
    <button class="back-link" @click="router.push('/')">← Back to Home</button>

    <section class="rules-hero">
      <p class="eyebrow">The little guide</p>
      <h1>Think small.<br />Play <span>clever.</span></h1>
      <p class="rules-intro">
        Nine little boards. One big strategy. Learn the twist that makes TAC2 different.
      </p>
      <div class="rule-badges">
        <span v-for="badge in badges" :key="badge">{{ badge }}</span>
      </div>
    </section>

    <section class="rules-section">
      <div class="section-heading">
        <p class="eyebrow">The basics</p>
        <h2>Three steps to get started</h2>
      </div>

      <div class="rule-cards">
        <article
          v-for="step in steps"
          :key="step.number"
          class="rule-card surface"
          :class="step.color"
        >
          <div class="rule-number">{{ step.number }}</div>
          <div class="mini-board">
            <span v-for="(mark, i) in step.board" :key="i">{{ mark }}</span>
          </div>
          <h3>{{ step.title }}</h3>
          <p>{{ step.text }}</p>
        </article>
      </div>
    </section>

    <section class="twist-section">
      <div class="twist-copy">
        <p class="eyebrow">The special twist</p>
        <h2>Your square decides their board.</h2>
        <p>
          Every square on a small board corresponds to another board in the larger 3 × 3 grid.
          If you play in the top-right square, your opponent goes to the top-right board.
        </p>
        <p>
          So don't just ask, “Where can I win?” Ask, “Where will my move send them?”
        </p>
      </div>

      <div class="twist-example">
        <div class="example-label">A move changes everything</div>
        <div class="big-board">
          <div
            v-for="(board, i) in exampleBoards"
            :key="i"
            class="small-board"
            :class="{ 'target-board': board.target }"
          >
            <span v-for="cell in 9" :key="cell">{{ board.marks[cell - 1] }}</span>
          </div>
        </div>
        <p class="example-caption">Play in a square, send your rival to the matching board.</p>
      </div>
    </section>

    <section class="tips-section">
      <p class="eyebrow">A few friendly reminders</p>
      <h2>Play smart, stay cozy.</h2>

      <div class="tip-list">
        <div v-for="tip in tips" :key="tip.title" class="tip-item surface">
          <span class="tip-icon">{{ tip.icon }}</span>
          <div>
            <h3>{{ tip.title }}</h3>
            <p>{{ tip.text }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="rules-cta">
      <div>
        <p class="eyebrow">Ready when you are</p>
        <h2>Let's make a move.</h2>
        <p>Put your new strategy to the test.</p>
      </div>
      <button class="button" @click="router.push('/')">Choose a game →</button>
    </section>
  </section>
</template>

<style scoped>
.how-to-play-page {
  padding: 30px 0 50px;
}

.back-link {
  margin-bottom: 28px;
  border: 0;
  background: transparent;
  color: var(--muted);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.back-link:hover {
  color: var(--teal-dark);
}

/* Big titles share the same font */
.rules-hero h1,
.section-heading h2,
.twist-copy h2,
.tips-section h2,
.rules-cta h2 {
  font-family: var(--font-title);
  font-weight: 800;
  line-height: 1.1;
}

/* ----- Hero ----- */
.rules-hero {
  padding: 54px 30px;
  border-radius: 32px;
  background: var(--teal-soft);
  text-align: center;
}

.rules-hero .eyebrow {
  margin-bottom: 12px;
}

.rules-hero h1 {
  font-size: clamp(42px, 6vw, 68px);
}

.rules-hero h1 span {
  color: var(--coral);
}

.rules-intro {
  max-width: 520px;
  margin: 20px auto 0;
  color: var(--muted);
  font-size: 18px;
}

.rule-badges {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 26px;
}

.rule-badges span {
  padding: 9px 15px;
  border-radius: var(--radius-pill);
  background: var(--paper);
  font-size: 13px;
  font-weight: 700;
}

/* ----- Three steps ----- */
.rules-section,
.tips-section {
  padding: 58px 0;
}

.section-heading {
  margin-bottom: 26px;
}

.section-heading h2,
.tips-section h2 {
  font-size: clamp(30px, 4vw, 42px);
}

.rule-cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.rule-card {
  padding: 24px;
  border-radius: var(--radius-md);
}

.rule-number {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  margin-bottom: 20px;
  border-radius: var(--radius-sm);
  background: var(--coral-soft);
  color: var(--coral);
  font-weight: 800;
}

.rule-card.teal .rule-number {
  background: var(--teal-soft);
  color: var(--teal-dark);
}

.rule-card.violet .rule-number {
  background: var(--violet-soft);
  color: var(--violet);
}

.mini-board {
  display: grid;
  grid-template-columns: repeat(3, 42px);
  width: fit-content;
  margin-bottom: 22px;
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
}

.mini-board span {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-right: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  color: var(--teal-dark);
  font-size: 24px;
  font-weight: 800;
}

.mini-board span:nth-child(3n) {
  border-right: 0;
}

.mini-board span:nth-child(n + 7) {
  border-bottom: 0;
}

.rule-card h3,
.tip-item h3 {
  margin-bottom: 8px;
  font-size: 19px;
}

.rule-card p,
.twist-copy > p:not(.eyebrow),
.tip-item p,
.rules-cta p:not(.eyebrow) {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.7;
}

/* ----- The twist ----- */
.twist-section {
  display: grid;
  grid-template-columns: 0.9fr 1.1fr;
  align-items: center;
  gap: 36px;
  padding: 38px;
  border-radius: 30px;
  background: var(--paper);
}

.twist-copy h2 {
  margin-bottom: 20px;
  font-size: clamp(32px, 4vw, 46px);
}

.twist-copy > p:not(.eyebrow) + p {
  margin-top: 14px;
}

.twist-example {
  min-width: 0;
  padding: 24px;
  border-radius: var(--radius-md);
  background: var(--cream);
}

.example-label {
  margin-bottom: 18px;
  font-size: 14px;
  font-weight: 800;
}

.big-board {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 5px;
  aspect-ratio: 1;
  max-width: 390px;
  margin: auto;
}

.small-board {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2px;
  padding: 4px;
  border-radius: 7px;
  background: var(--line);
}

.small-board span {
  display: grid;
  place-items: center;
  min-width: 0;
  aspect-ratio: 1;
  border-radius: 2px;
  background: var(--paper);
  color: var(--coral);
  font-size: clamp(10px, 2vw, 19px);
  font-weight: 800;
}

.small-board.target-board {
  outline: 3px solid var(--teal);
  outline-offset: -2px;
}

.example-caption {
  margin-top: 16px;
  color: var(--muted);
  font-size: 13px;
  text-align: center;
}

/* ----- Tips ----- */
.tips-section h2 {
  margin-bottom: 26px;
}

.tip-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 20px;
  border-radius: var(--radius-md);
}

.tip-icon {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  background: var(--gold-soft);
  color: var(--teal-dark);
}

/* ----- Call to action ----- */
.rules-cta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 30px;
  border-radius: var(--radius-lg);
  background: var(--teal-soft);
}

.rules-cta h2 {
  margin-bottom: 8px;
  font-size: 36px;
}

.rules-cta .button {
  border: 0;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  white-space: nowrap;
}

/* ----- Small screens ----- */
@media (max-width: 880px) {
  .rule-cards,
  .tip-list,
  .twist-section {
    grid-template-columns: 1fr;
  }

  .twist-section {
    padding: 24px;
  }
}

@media (max-width: 560px) {
  .rules-hero {
    padding: 38px 18px;
  }

  .rules-section,
  .tips-section {
    padding: 36px 0;
  }

  .twist-section {
    padding: 20px;
  }

  .twist-example {
    padding: 14px;
  }

  .rules-cta {
    align-items: flex-start;
    flex-direction: column;
    padding: 24px;
  }
}
</style>