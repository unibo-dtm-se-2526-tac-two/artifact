
<template>
  <section class="hero">
    <div class="hero-text">
      <p class="eyebrow">Think small. Win big.</p>
      <h1>Tic-tac-toe,<br />with a <span class="twist">twist.</span></h1>
      <p class="intro">
        Nine boards, one clever move at a time. Pick a square and decide where your rival
        plays next.
      </p>

      <div class="buttons">
        <a href="#modes" class="button">Choose a game →</a>
        <a href="/how-to-play" class="link-button">
          <span class="play-circle">
            <svg class="icon">
              <use href="/design/tac2-interface-icons.svg#play" />
            </svg>
          </span>
          How to play
        </a>
      </div>

      <p class="players">Join 2,460 thoughtful players</p>
    </div>

    <div class="hero-picture">
      <div class="circle"></div>
      <div class="sun"></div>
      <div class="tile tile-x">×</div>
      <div class="tile tile-o">○</div>
      <div class="tip">
        <strong>Tip!</strong> Every move sends your rival somewhere new.
      </div>
      <img class="mochi" src="/design/mochi-mascot.svg" alt="Mochi the cat" />
    </div>
  </section>
</template>

<script setup>
</script>
