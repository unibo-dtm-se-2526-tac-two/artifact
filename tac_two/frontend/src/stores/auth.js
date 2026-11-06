
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(sessionStorage.getItem('tac2_access_token'))
  const user = ref(null)
  const isAuthenticated = ref(false)
  const isLoading = ref(false)

  // Retrieve the currently authenticated user
  async function fetchUser() {
    if (!token.value) {
      user.value = null
      isAuthenticated.value = false
      return false
    }

    try {
      const response = await fetch('/api/v1/users/me', {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      })

      if (!response.ok) {
        logout()
        return false
      }

      user.value = await response.json()
      isAuthenticated.value = true
      return true
    } catch (error) {
      console.error('Could not retrieve user:', error)
      return false
    }
  }

  // Register a new account
  async function register(username, email, password) {
    const response = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        email,
        password,
      }),
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(getErrorMessage(data.detail))
    }

    return data
  }

  // Sign in
  async function login(email, password) {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(getErrorMessage(data.detail))
    }

    token.value = data.access_token
    sessionStorage.setItem('tac2_access_token', data.access_token)

    const success = await fetchUser()

    if (!success) {
      logout()
      throw new Error('Could not retrieve your account information.')
    }

    return user.value
  }

  // Sign out
  async function logout() {
    if (token.value) {
      try {
        await fetch('/api/v1/auth/logout', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token.value}`,
          },
        })
      } catch (error) {
        console.error('Logout request failed:', error)
      }
    }

    token.value = null
    user.value = null
    isAuthenticated.value = false
    sessionStorage.removeItem('tac2_access_token')
  }

  function getErrorMessage(detail) {
    if (typeof detail === 'string') {
      const messages = {
        REGISTER_USER_ALREADY_EXISTS: 'This email is already registered.',
        REGISTER_USERNAME_ALREADY_EXISTS: 'This username is already taken.',
        LOGIN_BAD_CREDENTIALS: 'Incorrect email or password.',
      }

      return messages[detail] || detail
    }

    if (Array.isArray(detail)) {
      return detail.map((item) => item.msg).join(' ')
    }

    if (detail?.reason) {
      return detail.reason
    }

    return 'Something went wrong. Please try again.'
  }

  return {
    token,
    user,
    isAuthenticated,
    isLoading,
    fetchUser,
    register,
    login,
    logout,
  }
})
