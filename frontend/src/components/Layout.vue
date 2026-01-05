<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAuthStore} from '@/stores/auth'
import {useAppStore} from '@/stores/app'
import {useMediaQuery} from '@vueuse/core'
import {Calendar, FileText, LogOut, Menu, Pill, Settings, Users, X} from 'lucide-vue-next'
import {Button} from '@/components/ui/button'

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const isDesktop = useMediaQuery('(min-width: 1024px)')

const sidebarOpen = ref(true)

onMounted(async () => {
  sidebarOpen.value = window.innerWidth >= 1024

  await appStore.fetchInitialData()
})

watch(isDesktop, (ehDesktop) => {
  sidebarOpen.value = ehDesktop
})

const dataAtual = new Date().toLocaleDateString('pt-BR', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric'
})

const allMenuItems = [
  {id: 'pacientes', path: '/pacientes', label: 'Pacientes', icon: Users},
  {id: 'agenda', path: '/agenda', label: 'Agenda', icon: Calendar},
  {id: 'farmacia', path: '/farmacia', label: 'Farmácia', icon: Pill},
  {id: 'relatorios', path: '/relatorios', label: 'Relatórios', icon: FileText},
  {id: 'ajustes', path: '/ajustes', label: 'Configurações', icon: Settings},
]

const menuItems = computed(() => {
  return allMenuItems.filter(item => {
    return authStore.hasAccess(item.id)
  })
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="flex h-screen bg-gray-50">
    <aside
        :class="sidebarOpen ? 'w-64' : 'w-0'"
        class="bg-blue-900 text-white <!--transition-all duration-300--> relative overflow-hidden flex flex-col"
    >
      <div class="p-4 flex-1 overflow-y-auto pb-32">
        <div class="flex items-center justify-between mb-6">
          <h1 class="text-xl font-semibold truncate">HC Quimioterapia</h1>
          <Button
              class="text-white hover:bg-blue-800 lg:hidden"
              size="icon"
              variant="ghost"
              @click="sidebarOpen = false"
          >
            <X class="h-5 w-5"/>
          </Button>
        </div>

        <div class="bg-blue-800/50 rounded-lg p-3 mb-6">
          <p class="text-xs text-blue-200 uppercase mb-1">Data</p>
          <p class="text-sm text-white leading-tight capitalize">
            {{ dataAtual }}
          </p>
        </div>

        <nav class="space-y-2">
          <router-link
              v-for="item in menuItems"
              :key="item.id"
              v-slot="{ navigate, isActive }"
              :to="item.path"
              custom
          >
            <button
                :class="isActive ? 'bg-blue-800 text-white' : 'text-blue-100 hover:bg-blue-800/50'"
                class="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors"
                @click="navigate"
            >
              <component :is="item.icon" class="h-5 w-5"/>
              <span>{{ item.label }}</span>
            </button>
          </router-link>
        </nav>
      </div>

      <div class="p-4 border-t border-blue-800 space-y-3 bg-blue-900">
        <div class="text-sm text-blue-200">
          <p class="truncate font-medium">{{ authStore.user?.nome }}</p>
          <p class="text-xs mt-1 truncate opacity-80">{{ authStore.user?.grupo }}</p>
        </div>
        <Button
            class="w-full text-blue-100 hover:bg-blue-800 hover:text-white justify-start"
            size="sm"
            variant="ghost"
            @click="handleLogout"
        >
          <LogOut class="h-4 w-4 mr-2"/>
          Sair
        </Button>
      </div>
    </aside>

    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white px-6 py-4 flex-shrink-0 flex items-center">
        <Button
            v-if="!sidebarOpen"
            class="-ml-2"
            size="icon"
            variant="ghost"
            @click="sidebarOpen = true"
        >
          <Menu class="h-5 w-5"/>
        </Button>
      </header>

      <main class="flex-1 overflow-y-auto p-6 bg-gray-50/50">
        <router-view/>
      </main>
    </div>
  </div>
</template>
