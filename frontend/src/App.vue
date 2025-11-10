<template>
  <component :is="layout">
    <router-view />
  </component>
  <LoadingIndicator />
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
const route = useRoute();

import { onMounted, computed } from 'vue';
import { useAuthStore } from './stores/auth';
import DefaultLayout from './layouts/DefaultLayout.vue';
import LoginLayout from './layouts/LoginLayout.vue';
import LoadingIndicator from './components/LoadingIndicator.vue';

const layout = computed(() => {
  return route.meta.layout === 'LoginLayout' ? LoginLayout : DefaultLayout;
});

const authStore = useAuthStore();
onMounted(async () => {
  await authStore.initializeAuth();
});
</script>
