
<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <section class="how-to-play-page">
    <button class="back-link" @click="router.push('/')">
      ← Back to Home
    </button>

    <section class="rules-hero">
      <p class="eyebrow">The little guide</p>
      <h1>Think small.<br />Play <span>clever.</span></h1>
      <p class="rules-intro">
        Nine little boards. One big strategy.
        Learn the twist that makes TAC2 different.
      </p>
      <div class="rule-badges">
        <span>✦ Easy to learn</span>
        <span>♟ Two players</span>
        <span>♡ Strategy first</span>
      </div>
    </section>

    <section class="rules-section">
      <div class="section-heading">
        <p class="eyebrow">The basics</p>
        <h2>Three steps to get started</h2>
      </div>

      <div class="rule-cards">
        <article class="rule-card coral">
          <div class="rule-number">01</div>
          <div class="mini-board">
            <span>×</span><span></span><span>○</span>
            <span></span><span>×</span><span></span>
            <span>○</span><span></span><span></span>
          </div>
          <h3>Take your turn</h3>
          <p>Players take turns placing their mark, X or O, in an empty square.</p>
        </article>

        <article class="rule-card teal">
          <div class="rule-number">02</div>
          <div class="mini-board">
            <span></span><span>×</span><span></span>
            <span></span><span>○</span><span></span>
            <span></span><span>×</span><span></span>
          </div>
          <h3>Think one move ahead</h3>
          <p>Your move determines which small board your opponent must play in next.</p>
        </article>

        <article class="rule-card violet">
          <div class="rule-number">03</div>
          <div class="mini-board winning-board">
            <span>×</span><span>×</span><span>×</span>
            <span>○</span><span>○</span><span></span>
            <span></span><span></span><span></span>
          </div>
          <h3>Win the big board</h3>
          <p>
            Win small boards by making three in a row.
            Win the overall game by claiming three small boards in a row.
          </p>
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
          So don't just ask, “Where can I win?”
          Ask, “Where will my move send them?”
        </p>
      </div>

      <div class="twist-example">
        <div class="example-label">A move changes everything</div>
        <div class="big-board">
          <div class="small-board">
            <span></span><span></span><span></span>
            <span></span><span>×</span><span></span>
            <span></span><span></span><span></span>
          </div>
          <div class="small-board"><span></span><span></span><span></span><span></span><span>○</span><span></span><span></span><span></span><span></span></div>
          <div class="small-board"><span></span><span>×</span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
          <div class="small-board"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
          <div class="small-board"><span></span><span></span><span></span><span></span><span>○</span><span></span><span></span><span></span><span></span></div>
          <div class="small-board target-board"><span></span><span></span><span></span><span></span><span>×</span><span></span><span></span><span></span><span></span></div>
          <div class="small-board"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
          <div class="small-board"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
          <div class="small-board"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
        </div>
        <p class="example-caption">
          Play in a square, send your rival to the matching board.
        </p>
      </div>
    </section>

    <section class="tips-section">
      <p class="eyebrow">A few friendly reminders</p>
      <h2>Play smart, stay cozy.</h2>

      <div class="tip-list">
        <div class="tip-item">
          <span class="tip-icon">✦</span>
          <div>
            <h3>Plan ahead</h3>
            <p>Think about your next move and your opponent's options.</p>
          </div>
        </div>

        <div class="tip-item">
          <span class="tip-icon">♡</span>
          <div>
            <h3>Watch the whole board</h3>
            <p>A small-board win can bring you closer to the big one.</p>
          </div>
        </div>

        <div class="tip-item">
          <span class="tip-icon">☁</span>
          <div>
            <h3>Enjoy the game</h3>
            <p>Every round is a chance to learn a new strategy.</p>
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
      <button class="button" @click="router.push('/')">
        Choose a game →
      </button>
    </section>
  </section>
</template>
