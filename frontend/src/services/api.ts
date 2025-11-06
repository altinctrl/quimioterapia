import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const api = axios.create({
  baseURL: '/', // Adjust if your API is on a different host
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor to add the access token to every request
api.interceptors.request.use(config => {
  const authStore = useAuthStore();
  const token = authStore.accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

// Response error interceptor to handle expired tokens
api.interceptors.response.use(
  response => response, // Simply return successful responses
  async error => {
    const originalRequest = error.config;
    const authStore = useAuthStore();

    // Check if the error is 401 and it's not a retry request
    if (error.response.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise(function(resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true; // Mark it as a retry
      isRefreshing = true;

      try {
        console.log('Access token expired. Attempting to refresh...');
        const { data } = await axios.post('/api/token/refresh');
        
        // Set the new token in the store
        authStore.setToken(data.access_token);
        
        // Update the authorization header of the original request
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        
        processQueue(null, data.access_token);
        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        console.error('Unable to refresh token. Logging out.', refreshError);
        const router = (await import('../router')).default;
        authStore.logout(router); // If refresh fails, logout the user
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // For other errors, just reject the promise
    return Promise.reject(error);
  }
);

export default api;