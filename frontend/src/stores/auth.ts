import {defineStore} from 'pinia'
import {computed, ref} from 'vue'
import api from '@/services/api'
import type {User, UserRole} from '@/types'

function mapGroupsToRole(groups: string[]): UserRole {
  if (groups.includes('Farmacia')) return 'farmacia'
  if (groups.includes('Medicos')) return 'medico'
  if (groups.includes('GLO-SEC-HCPE-SETISD') || groups.includes('Admins')) return 'admin'
  return 'enfermeiro'
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User & { token?: string } | null>(null)

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

      const token = responseToken.data.access_token

      const responseUser = await api.get('/api/users/me', {
        headers: {Authorization: `Bearer ${token}`}
      })

      const userDataBackend = responseUser.data

      const userRole = mapGroupsToRole(userDataBackend.groups || [])

      const userObj = {
        id: userDataBackend.username,
        nome: userDataBackend.displayName ? userDataBackend.displayName[0] : userDataBackend.username,
        username: userDataBackend.username,
        email: userDataBackend.email,
        grupo: userDataBackend.groups ? userDataBackend.groups.join(', ') : '',
        role: userRole,
        token: token
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

  function logout() {
    user.value = null
    localStorage.removeItem('user')
    // api.post('/api/logout')
  }

  function hasAccess(page: string): boolean {
    if (!user.value) return false

    const rolePermissions: Record<UserRole, string[]> = {
      'enfermeiro': ['dashboard', 'pacientes', 'agenda', 'agendamento', 'ajustes', 'relatorios', 'protocolos'],
      'medico': ['pacientes', 'prescricao', 'protocolos'],
      'farmacia': ['farmacia', 'pacientes', 'relatorios'],
      'admin': ['dashboard', 'pacientes', 'agenda', 'agendamento', 'farmacia', 'relatorios', 'protocolos', 'ajustes', 'prescricao']
    }

    const permissions = rolePermissions[user.value.role]
    return permissions ? permissions.includes(page) : false
  }

  return {
    user, isAuthenticated, login, logout, hasAccess
  }
})