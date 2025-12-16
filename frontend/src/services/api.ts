import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000', headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use((config) => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const userData = JSON.parse(userStr)
      if (userData.token) {
        config.headers.Authorization = `Bearer ${userData.token}`
      }
    } catch (e) {
      console.error('Erro ao ler token do localStorage', e)
    }
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

api.interceptors.response.use((response) => {
  return response
}, (error) => {
  if (error.response && error.response.status === 401) {
    if (!window.location.pathname.includes('/login')) {
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
  }
  return Promise.reject(error)
})

export default api