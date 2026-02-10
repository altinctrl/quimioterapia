import {defineStore} from 'pinia'
import {computed, ref} from 'vue'
import api from '@/services/api'
import type {User, UserRole} from '@/types/typesAuth.ts'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User & { token?: string, refreshToken?: string } | null>(null)
  const isJustLoggedIn = ref(false)

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
        registro: userDataBackend.registroProfissional || '',
        token: data.access_token,
        refreshToken: data.refresh_token
      }
      user.value = userObj
      isJustLoggedIn.value = true
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

  async function atualizarRegistro(novoRegistro: string): Promise<boolean> {
    if (!user.value) return false
    try {
      const tipo = user.value.role === 'medico' ? 'CRM' : 'COREN'

      const response = await api.patch('/api/users/me/registro', {
        registro_profissional: novoRegistro,
        tipo_registro: tipo
      })

      user.value.registro = response.data.registroProfissional
      localStorage.setItem('user', JSON.stringify(user.value))
      return true
    } catch (error) {
      console.error('Erro ao atualizar registro', error)
      return false
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
    user, isJustLoggedIn, isAuthenticated, login, atualizarRegistro, updateTokens, logout, hasAccess
  }
})
