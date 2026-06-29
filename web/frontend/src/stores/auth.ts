import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'

interface User {
  id: number
  email: string
  benutzername: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<User | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(email: string, passwort: string) {
    const data = await api.post<{ access_token: string }>('/auth/login', { email, passwort })
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    await fetchUser()
  }

  async function register(email: string, benutzername: string, passwort: string) {
    await api.post('/auth/register', { email, benutzername, passwort })
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      user.value = await api.get<User>('/auth/me')
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  if (token.value) {
    fetchUser()
  }

  return { token, user, isLoggedIn, login, register, fetchUser, logout }
})
