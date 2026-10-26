<script setup>
import { ref } from 'vue'

const ICONS = '/design/tac2-extra-icons.svg' // icon file in public/design

const mode = ref('signin') // 'signin' | 'signup' | 'forgot'
const showPassword = ref(false)
const name = ref('')
const email = ref('')
const password = ref('')
const message = ref(null) // { type: 'error' | 'info', text: '...' }

function setMode(newMode) {
  mode.value = newMode
  message.value = null
}

function submitForm() {
  message.value = null

  if (mode.value === 'signup' && !name.value.trim()) {
    message.value = { type: 'error', text: 'Please choose a display name.' }
    return
  }
  if (!email.value.trim() || !email.value.includes('@')) {
    message.value = { type: 'error', text: 'Please enter a valid email address.' }
    return
  }
  if (mode.value !== 'forgot' && !password.value) {
    message.value = { type: 'error', text: 'Please enter your password.' }
    return
  }
  if (mode.value === 'signup' && password.value.length < 8) {
    message.value = { type: 'error', text: 'Use at least 8 characters for your password.' }
    return
  }

  // TODO: send this to the backend (sign in, create account or send a reset link).
  message.value = { type: 'info', text: 'The form is ready. The backend is not connected yet.' }
}

function googleSignIn() {
  // TODO: Google sign-in
  message.value = { type: 'info', text: 'Google sign-in is not connected yet.' }
}
</script>

<template>
  <div class="auth-screen">
    <!-- Left side: mascot -->
    <div class="auth-left">
      <div class="deco-tile tile-one">×</div>
      <div class="deco-tile tile-two">○</div>
      <div class="auth-circle circle-one"></div>
      <div class="auth-circle circle-two"></div>

      <div class="auth-mascot-wrap">
        <img src="/design/mochi-mascot.svg" alt="Mochi the cat" />
      </div>

      <div class="auth-left-copy">
        <div class="auth-brand">
          <div class="brand-mark"><span>T</span><span>2</span></div>
          <div class="brand-name">Tac<span>2</span></div>
        </div>
        <p class="auth-tagline">
          Nine boards, one clever move at a time. Every square is a choice.
        </p>
        <div class="auth-trust">
          <span>2,460 players</span>
          <span>Spring season</span>
        </div>
      </div>
    </div>

    <!-- Right side: form -->
    <div class="auth-right">
      <div class="auth-form-box">
        <RouterLink to="/" class="auth-back">← Back to Tac2</RouterLink>

        <div class="auth-tabs">
          <button type="button" :class="{ active: mode === 'signin' }" @click="setMode('signin')">
            Sign in
          </button>
          <button type="button" :class="{ active: mode === 'signup' }" @click="setMode('signup')">
            Create account
          </button>
        </div>

        <h1 class="auth-heading">
          {{ mode === 'signin' ? 'Welcome back!' : mode === 'signup' ? 'Join the game' : 'Reset your password' }}
        </h1>
        <p class="auth-subheading">
          {{
            mode === 'signin'
              ? 'Sign in to continue your clever streak.'
              : mode === 'signup'
                ? 'Create your account to track matches and climb the board.'
                : 'Enter your email and we’ll send you a reset link.'
          }}
        </p>

        <form class="auth-form" novalidate @submit.prevent="submitForm">
          <div v-if="mode === 'signup'" class="input-group">
            <label for="auth-name">Display name</label>
            <div class="input-wrap">
              <svg class="icon"><use :href="ICONS + '#user'" /></svg>
              <input
                id="auth-name"
                v-model="name"
                class="auth-input"
                type="text"
                placeholder="Sofia Scardovi"
                autocomplete="name"
              />
            </div>
          </div>

          <div class="input-group">
            <label for="auth-email">Email address</label>
            <div class="input-wrap">
              <svg class="icon"><use :href="ICONS + '#mail'" /></svg>
              <input
                id="auth-email"
                v-model="email"
                class="auth-input"
                type="email"
                placeholder="sofia@example.com"
                autocomplete="email"
              />
            </div>
          </div>

          <div v-if="mode !== 'forgot'" class="input-group">
            <label for="auth-password">Password</label>
            <div class="input-wrap">
              <svg class="icon"><use :href="ICONS + '#lock'" /></svg>
              <input
                id="auth-password"
                v-model="password"
                class="auth-input"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                :autocomplete="mode === 'signin' ? 'current-password' : 'new-password'"
              />
              <button
                type="button"
                class="pw-toggle"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
                @click="showPassword = !showPassword"
              >
                <svg class="icon"><use :href="ICONS + '#' + (showPassword ? 'eye-off' : 'eye')" /></svg>
              </button>
            </div>
          </div>

          <button v-if="mode === 'signin'" type="button" class="forgot-link" @click="setMode('forgot')">
            Forgot password?
          </button>

          <p v-if="message" class="auth-message" :class="message.type" role="status">
            {{ message.text }}
          </p>

          <button type="submit" class="auth-submit-btn">
            {{ mode === 'signin' ? 'Sign in' : mode === 'signup' ? 'Create account' : 'Send reset link' }}
            <svg class="icon"><use :href="ICONS + '#arrow'" /></svg>
          </button>
        </form>

        <template v-if="mode !== 'forgot'">
          <div class="auth-divider"><span>or continue with</span></div>

          <button type="button" class="google-btn" @click="googleSignIn">
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
            </svg>
            Continue with Google
          </button>
        </template>

        <p class="auth-switch">
          {{
            mode === 'signin'
              ? 'New here? '
              : mode === 'signup'
                ? 'Already have an account? '
                : 'Remembered your password? '
          }}
          <button type="button" @click="setMode(mode === 'signin' ? 'signup' : 'signin')">
            {{ mode === 'signin' ? 'Create an account' : 'Sign in instead' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-screen {
  display: grid;
  grid-template-columns: 400px 1fr;
  min-height: 100vh;
}

/* ----- Left side ----- */
.auth-left {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 44px;
  overflow: hidden;
  background: linear-gradient(155deg, #163e3a 0%, #2a7068 100%);
  color: white;
}

.auth-circle {
  position: absolute;
  border: 2px solid rgba(255, 255, 255, 0.08);
  border-radius: 50%;
  pointer-events: none;
}

.circle-one {
  top: -90px;
  left: -90px;
  width: 320px;
  height: 320px;
}

.circle-two {
  right: -50px;
  bottom: 200px;
  width: 200px;
  height: 200px;
}

.deco-tile {
  position: absolute;
  display: grid;
  place-items: center;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  font-family: var(--font-title);
  font-weight: 700;
}

.tile-one {
  top: 32px;
  right: 28px;
  width: 68px;
  height: 68px;
  font-size: 38px;
}

.tile-two {
  top: 130px;
  right: 96px;
  width: 50px;
  height: 50px;
  font-size: 30px;
}

.auth-mascot-wrap {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  height: 270px;
}

.auth-mascot-wrap img {
  width: 210px;
  filter: drop-shadow(0 20px 35px rgba(0, 0, 0, 0.3));
}

.auth-left-copy {
  position: relative;
  z-index: 2;
  margin-top: 22px;
}

.auth-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.brand-mark {
  display: grid;
  grid-template-columns: 1fr 1fr;
  place-items: center;
  width: 36px;
  height: 36px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 11px;
  font-family: var(--font-title);
  font-weight: 700;
  transform: rotate(-3deg);
}

.brand-mark span:last-child {
  align-self: end;
  padding-bottom: 3px;
  color: var(--gold);
  font-size: 13px;
}

.brand-name {
  font-family: var(--font-title);
  font-size: 25px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.7px;
}

.brand-name span {
  color: var(--gold);
}

.auth-tagline {
  max-width: 320px;
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.78;
}

.auth-trust {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.auth-trust span {
  padding: 5px 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.1);
  font-size: 11px;
  font-weight: 600;
}

/* ----- Right side ----- */
.auth-right {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 40px;
  background: var(--cream);
}

.auth-form-box {
  width: 100%;
  max-width: 430px;
}

.auth-back {
  display: inline-block;
  margin-bottom: 18px;
  color: var(--teal);
  font-size: 12px;
  font-weight: 700;
}

.auth-tabs {
  display: flex;
  padding: 4px;
  margin-bottom: 26px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: var(--paper);
}

.auth-tabs button {
  flex: 1;
  height: 38px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: var(--muted);
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.auth-tabs button.active {
  background: white;
  color: var(--ink);
  box-shadow: 0 2px 8px rgba(41, 59, 58, 0.08);
}

.auth-heading {
  font-family: var(--font-title);
  font-size: clamp(26px, 3vw, 34px);
  line-height: 1.1;
  letter-spacing: -0.8px;
}

.auth-subheading {
  margin: 6px 0 24px;
  color: var(--muted);
  font-size: 14px;
  line-height: 1.5;
}

/* ----- Form ----- */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.input-group label {
  font-size: 12px;
  font-weight: 700;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrap > svg {
  position: absolute;
  left: 14px;
  width: 16px;
  height: 16px;
  color: var(--muted);
  pointer-events: none;
}

.auth-input {
  width: 100%;
  height: 50px;
  padding: 0 46px 0 42px;
  border: 1.5px solid var(--line);
  border-radius: var(--radius-sm);
  background: var(--paper);
  color: var(--ink);
  font: inherit;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.auth-input:focus {
  border-color: var(--teal);
  box-shadow: 0 0 0 3px rgba(47, 138, 127, 0.1);
}

.auth-input::placeholder {
  color: var(--muted);
}

.pw-toggle {
  position: absolute;
  right: 12px;
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  padding: 0;
  border: none;
  border-radius: 8px;
  background: none;
  color: var(--muted);
  cursor: pointer;
}

.pw-toggle svg {
  width: 15px;
  height: 15px;
}

.pw-toggle:hover {
  background: var(--cream);
  color: var(--ink);
}

.forgot-link {
  align-self: flex-end;
  margin-top: -4px;
  border: none;
  background: none;
  color: var(--teal);
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.forgot-link:hover {
  text-decoration: underline;
}

.auth-message {
  padding: 11px 14px;
  border-radius: 12px;
  font-size: 13px;
}

.auth-message.error {
  background: var(--coral-soft);
  color: var(--danger);
}

.auth-message.info {
  background: var(--teal-soft);
  color: var(--teal-dark);
}

.auth-submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  height: 52px;
  margin-top: 4px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--teal);
  color: white;
  font: inherit;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 9px 22px rgba(47, 138, 127, 0.24);
  transition: transform 0.2s, box-shadow 0.2s;
}

.auth-submit-btn svg {
  width: 17px;
  height: 17px;
}

.auth-submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 13px 26px rgba(47, 138, 127, 0.3);
}

.auth-divider {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 20px 0;
  color: var(--muted);
  font-size: 12px;
}

.auth-divider::before,
.auth-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--line);
}

.google-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  height: 50px;
  border: 1.5px solid var(--line);
  border-radius: var(--radius-sm);
  background: var(--paper);
  color: var(--ink);
  font: inherit;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.google-btn:hover {
  border-color: rgba(41, 59, 58, 0.25);
  box-shadow: 0 4px 14px rgba(41, 59, 58, 0.07);
}

.auth-switch {
  margin-top: 18px;
  color: var(--muted);
  font-size: 13px;
  text-align: center;
}

.auth-switch button {
  border: none;
  background: none;
  color: var(--teal);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.auth-switch button:hover {
  text-decoration: underline;
}

/* ----- Small screens: only the form ----- */
@media (max-width: 1000px) {
  .auth-screen {
    grid-template-columns: 340px 1fr;
  }
}

@media (max-width: 760px) {
  .auth-screen {
    grid-template-columns: 1fr;
  }

  .auth-left {
    display: none;
  }

  .auth-right {
    padding: 36px 24px;
  }
}
</style>