import {defineStore} from 'pinia'
import {computed, ref} from 'vue'
import api from '@/services/api'
import type {User, UserRole} from '@/types/typesAuth.ts'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User & { token?: string, refreshToken?: string } | null>(null)

  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    try {
      user.value = JSON.parse(savedUser)
    } catch (e) {
      localStorage.removeItem('user')
    }
  }

  const isAuthenticated = computed(() => !!user.value)

  async function login(username: string, password: string): Promise<{ success: boolean; error?: string }> {
    try {
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)

      const responseToken = await api.post('/api/login', formData, {
        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
      })

      const data = responseToken.data
      const responseUser = await api.get('/api/users/me', {
        headers: {Authorization: `Bearer ${data.access_token}`}
      })
      const userDataBackend = responseUser.data
      const userObj = {
        id: userDataBackend.username,
        nome: userDataBackend.displayName || userDataBackend.username,
        username: userDataBackend.username,
        email: userDataBackend.email,
        grupo: userDataBackend.groups ? userDataBackend.groups.join(', ') : '',
        role: userDataBackend.role as UserRole,
        token: data.access_token,
        refreshToken: data.refresh_token
      }
      user.value = userObj
      localStorage.setItem('user', JSON.stringify(userObj))
      return {success: true}
    } catch (err: any) {
      console.error('Erro no login:', err)
      if (err.response && err.response.status === 401) {
        return {success: false, error: 'Usuário ou senha incorretos'}
      }
      return {success: false, error: 'Erro de conexão com o servidor'}
    }
  }

  function updateTokens(accessToken: string, refreshToken: string) {
    if (user.value) {
      user.value.token = accessToken
      user.value.refreshToken = refreshToken
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  async function logout() {
    try {
      if (user.value?.refreshToken) {
        await api.post('/api/logout', {
          refresh_token: user.value.refreshToken
        })
      }
    } catch (error) {
      console.error('Erro ao invalidar token no servidor', error)
    } finally {
      user.value = null
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
  }

  function hasAccess(page: string): boolean {
    if (!user.value) return false
    const rolePermissions: Record<UserRole, string[]> = {
      'enfermeiro': ['dashboard', 'pacientes', 'agenda', 'agendamento', 'ajustes', 'relatorios', 'protocolos', 'equipe'],
      'medico': ['pacientes', 'prescricao', 'protocolos'],
      'farmacia': ['farmacia', 'pacientes', 'relatorios'],
      'admin': ['dashboard', 'pacientes', 'agenda', 'agendamento', 'farmacia', 'relatorios', 'protocolos', 'ajustes', 'prescricao', 'equipe']
    }
    const permissions = rolePermissions[user.value.role]
    return permissions ? permissions.includes(page) : false
  }

  return {
    user, isAuthenticated, login, updateTokens, logout, hasAccess
  }
})
