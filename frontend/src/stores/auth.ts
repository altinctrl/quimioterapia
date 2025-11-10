import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';

interface User {
  username: string;
  groups: string[];
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('accessToken') || null);
  const user = ref<User | null>(null);

  const isAuthenticated = computed(() => !!accessToken.value);
  const isAdmin = computed(() => {
    const ADMIN_GROUP = "GLO-SEC-HCPE-SETISD"; 
    return user.value?.groups?.includes(ADMIN_GROUP) || false;
  });

  function setToken(token: string) {
    accessToken.value = token;
    localStorage.setItem('accessToken', token);
  }

  function clearToken() {
    accessToken.value = null;
    localStorage.removeItem('accessToken');
    user.value = null;
  }

  function setUser(userData: User | null) {
    user.value = userData;
  }

  async function fetchUser() {
    if (!accessToken.value) {
      setUser(null);
      return;
    }
    try {
      const { data } = await api.get('/api/users/me');
      setUser(data);
    } catch (error) {
      console.error("Failed to fetch user info:", error);
      clearToken(); // Clear token if user info fetch fails
    }
  }

  async function login(username: string, password: string, rememberMe: boolean) {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    if (rememberMe) {
      params.append('remember_me', 'true');
    }

    const { data } = await api.post('/api/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    setToken(data.access_token);
    await fetchUser(); // Fetch user info immediately after login
  }

  async function logout(router?: any) {
    try {
      await api.post('/api/logout');
    } catch (error) {
      console.error("Logout failed, but clearing token anyway.", error);
    } finally {
      clearToken();
      if (router) {
        router.push({ name: 'Login' });
      }
    }
  }

  async function initializeAuth() {
    if (accessToken.value) {
      // If a token exists in localStorage, validate it by fetching user info
      await fetchUser();
    } else {
      // If no token, try to get a new one using the refresh token cookie
      try {
        const { data } = await api.post('/api/token/refresh');
        if (data.access_token) {
          setToken(data.access_token);
          await fetchUser(); // Fetch user info with the new token
        }
      } catch (error) {
        // It's okay if this fails - it just means the user doesn't have a valid refresh token
        console.log("No valid refresh token found.");
      }
    }
  }

  return { 
    accessToken, 
    user, 
    isAuthenticated, 
    isAdmin, 
    login, 
    logout,
    setToken,
    clearToken,
    fetchUser,
    initializeAuth
  };
});
