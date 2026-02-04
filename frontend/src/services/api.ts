import axios from 'axios'
import {useAuthStore} from '@/stores/storeAuth'
import router from '@/router'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

let isRefreshing = false
let failedQueue: any[] = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  const token = authStore.user?.token

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const authStore = useAuthStore()

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({resolve, reject})
        })
          .then(token => {
            originalRequest.headers['Authorization'] = 'Bearer ' + token
            return api(originalRequest)
          })
          .catch(err => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      return new Promise(async (resolve, reject) => {
        try {
          const response = await axios.post('http://localhost:8000/api/refresh', {
            refresh_token: authStore.user?.refreshToken
          })
          const {access_token, refresh_token} = response.data
          authStore.updateTokens(access_token, refresh_token)
          originalRequest.headers['Authorization'] = 'Bearer ' + access_token
          processQueue(null, access_token)
          resolve(api(originalRequest))
        } catch (refreshError) {
          processQueue(refreshError, null)
          await authStore.logout()
          void router.push('/login')
          reject(refreshError)
        } finally {
          isRefreshing = false
        }
      })
    }
    return Promise.reject(error)
  }
)

export default api
