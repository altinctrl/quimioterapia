<template>
  <component :is="layout">
    <router-view />
  </component>
  <LoadingIndicator />
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import DefaultLayout from './layouts/DefaultLayout.vue';
import LoginLayout from './layouts/LoginLayout.vue';
import LoadingIndicator from './components/LoadingIndicator.vue';

const route = useRoute();

const layout = computed(() => {
  switch (route.meta.layout) {
    case 'LoginLayout':
      return LoginLayout;
    default:
      return DefaultLayout;
  }
});
</script>
