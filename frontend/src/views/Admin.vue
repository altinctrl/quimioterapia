<template>
  <Card>
    <div v-if="authStore.isAdmin">
      <h1 class="text-2xl font-bold text-green-600">Admin Area</h1>
      <p class="mt-4">Welcome, administrator! This content is only visible to users with admin privileges.</p>
      <div v-if="authStore.user" class="mt-6 p-4 bg-gray-100 rounded">
        <h3 class="font-bold">User Information (from AD):</h3>
        <pre class="text-sm whitespace-pre-wrap">{{ JSON.stringify(authStore.user, null, 2) }}</pre>
      </div>
    </div>
    <div v-else>
      <h1 class="text-2xl font-bold text-red-600">Access Denied</h1>
      <p class="mt-4">You do not have sufficient privileges to view this page.</p>
    </div>
  </Card>
</template>

<script setup lang="ts">
import Card from '../components/Card.vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
</script>