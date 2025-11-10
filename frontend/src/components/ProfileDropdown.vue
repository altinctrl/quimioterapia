<template>
  <div class="relative">
    <button @click="isOpen = !isOpen" class="relative z-10 block h-10 w-10 rounded-full overflow-hidden border-2 border-gray-600 focus:outline-none focus:border-white">
      <UserCircleIcon class="h-full w-full text-gray-600" />
    </button>

    <div v-if="isOpen" @click="isOpen = false" class="fixed inset-0 h-full w-full z-10"></div>

    <div v-if="isOpen" class="absolute right-0 mt-2 w-72 bg-white rounded-lg shadow-xl z-20">
      <div class="p-4">
        <div class="flex items-center space-x-4">
          <div class="flex-shrink-0">
            <UserCircleIcon class="h-14 w-14 text-gray-600" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-lg font-semibold text-paper-text truncate">{{ authStore.user?.givenName?.[0] || authStore.user?.username || 'User' }}</p>
            <p class="text-sm text-gray-500 truncate">{{ authStore.user?.userPrincipalName?.[0] || 'N/A' }}</p>
          </div>
        </div>
      </div>
      
      <div class="border-t border-gray-200">
        <div class="p-4 space-y-3 text-sm text-paper-text">
          <div class="flex items-center">
            <BriefcaseIcon class="h-5 w-5 mr-3 text-gray-400" />
            <span class="flex-1"><span class="font-medium">Cargo:</span> {{ authStore.user?.title?.[0] || 'N/A' }}</span>
          </div>
          <div class="flex items-center">
            <BuildingOffice2Icon class="h-5 w-5 mr-3 text-gray-400" />
            <span class="flex-1"><span class="font-medium">Setor:</span> {{ authStore.user?.department?.[0] || 'N/A' }}</span>
          </div>
          <div class="flex items-center">
            <IdentificationIcon class="h-5 w-5 mr-3 text-gray-400" />
            <span class="flex-1"><span class="font-medium">Matrícula:</span> {{ authStore.user?.employeeNumber?.[0] || 'N/A' }}</span>
          </div>
        </div>
      </div>

      <div class="border-t border-gray-200 bg-gray-50 rounded-b-lg">
        <a href="#" @click.prevent="handleLogout" class="flex items-center justify-center px-4 py-3 text-sm font-medium text-paper-text hover:bg-paper-hover hover:text-paper-primary transition duration-150 ease-in-out">
          <ArrowLeftOnRectangleIcon class="h-5 w-5 mr-2" />
          <span>Logout</span>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { UserCircleIcon, ArrowLeftOnRectangleIcon, BriefcaseIcon, BuildingOffice2Icon, IdentificationIcon } from '@heroicons/vue/24/outline';
import { useAuthStore } from '../stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const isOpen = ref(false);

const handleLogout = async () => {
  await authStore.logout(router);
};

// Close dropdown on navigation
watch(() => route.path, () => {
  isOpen.value = false;
});
</script>
