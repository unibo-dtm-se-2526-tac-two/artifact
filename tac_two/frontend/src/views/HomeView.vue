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

<style scoped>
.hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  align-items: center;
  padding: 64px 0 80px;
}

.hero h1 {
  font-family: var(--font-title);
  font-size: 80px;
  font-weight: 800;
  line-height: 1.05;
}

.twist {
  color: var(--coral);
}

.intro {
  max-width: 420px;
  margin-top: 28px;
  color: var(--muted);
  font-size: 20px;
}

.buttons {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-top: 36px;
}

.link-button {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 700;
}

.play-circle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border: 1px solid var(--line);
  border-radius: 50%;
  background: var(--paper);
  color: var(--coral);
}

.players {
  margin-top: 40px;
  color: var(--muted);
}

/* The picture on the right */
.hero-picture {
  position: relative;
  aspect-ratio: 1 / 0.95;
}

.circle {
  position: absolute;
  top: 8%;
  right: 4%;
  bottom: 0;
  left: 8%;
  border-radius: 50%;
  background: var(--teal-soft);
}

.sun {
  position: absolute;
  top: 2%;
  right: 3%;
  width: 22%;
  aspect-ratio: 1;
  border-radius: 50%;
  background: var(--gold-soft);
}

.mochi {
  position: absolute;
  bottom: 2%;
  left: 50%;
  width: 62%;
  transform: translateX(-50%);
}

.tile {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: var(--paper);
  box-shadow: var(--shadow);
  font-size: 40px;
  line-height: 1;
}

.tile-x {
  top: 6%;
  left: 8%;
  color: var(--coral);
  transform: rotate(-8deg);
}

.tile-o {
  right: 2%;
  bottom: 6%;
  color: var(--teal);
  transform: rotate(6deg);
}

.tip {
  position: absolute;
  top: 24%;
  right: 0;
  max-width: 230px;
  padding: 14px 18px;
  border-radius: var(--radius-md);
  background: var(--paper);
  box-shadow: var(--shadow);
  color: var(--muted);
  font-size: 15px;
}

.tip strong {
  display: block;
  color: var(--coral);
}

@media (max-width: 880px) {
  .hero {
    grid-template-columns: 1fr;
    padding: 40px 0 56px;
  }

  .hero h1 {
    font-size: 52px;
  }

  .buttons {
    flex-wrap: wrap;
  }

  .hero-picture {
    width: 100%;
    max-width: 460px;
    margin: 0 auto;
  }
}
</style>