<template>
  <div v-if="isLoading" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
    <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-white"></div>
  </div>
</template>

<script setup lang="ts">
import { useUiStore } from '../stores/ui';
import { storeToRefs } from 'pinia';

const uiStore = useUiStore();
const { isLoading } = storeToRefs(uiStore);
</script>
