<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useAuthStore} from '@/stores/storeAuth.ts'
import {useMediaQuery} from '@vueuse/core'
import {AlertTriangle, Calendar, FileText, LogOut, Menu, Pill, Settings, Stethoscope, Users, X} from 'lucide-vue-next'
import {Button} from '@/components/ui/button'
import {useConfiguracaoStore} from "@/stores/storeAjustes.ts";
import ModalPerfilUsuario from "@/components/comuns/ModalPerfilUsuario.vue";

const router = useRouter()
const authStore = useAuthStore()
const configStore = useConfiguracaoStore()

const isDesktop = useMediaQuery('(min-width: 1024px)')

const sidebarOpen = ref(true)
const showProfileModal = ref(false)

onMounted(async () => {
  sidebarOpen.value = window.innerWidth >= 1024
  await configStore.fetchConfiguracoes()

  const user = authStore.user
  if (user && !user.registro && authStore.isJustLoggedIn) {
    if (user.role === 'medico' || user.role === 'enfermeiro') {
      showProfileModal.value = true
      authStore.isJustLoggedIn = false
    }
  }
})

const needsRegistroBanner = computed(() => {
  return authStore.user?.role === 'medico' && !authStore.user?.registro
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
  {id: 'equipe', path: '/equipe', label: 'Equipe', icon: Stethoscope},
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
  <div class="flex h-screen bg-gray-50 flex-col">
    <div
        v-if="needsRegistroBanner"
        class="bg-orange-100 border-b border-orange-200 text-orange-800 px-4 py-2 text-sm flex items-center justify-center gap-2"
    >
      <AlertTriangle class="h-4 w-4"/>
      <span>Seu cadastro está incompleto. O número do CRM é necessário para realizar prescrições.</span>
      <button
          class="underline font-semibold hover:text-orange-900"
          @click="showProfileModal = true"
      >
        Completar agora
      </button>
    </div>

    <div class="flex-1 flex overflow-hidden">
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
          <div
              class="text-sm text-blue-200 cursor-pointer hover:bg-blue-800/50 p-2 rounded transition-colors -mx-2"
              @click="showProfileModal = true"
          >
            <p class="truncate font-medium flex items-center justify-between">
              {{ authStore.user?.nome }}
              <span
                  v-if="authStore.user?.role && ['medico', 'enfermeiro'].includes(authStore.user?.role) && !authStore.user?.registro"
                  class="h-2 w-2 rounded-full bg-orange-400 block"></span>
            </p>
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
        <header class="bg-gray-50/50 px-6 py-4 flex-shrink-0 flex items-center">
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

    <ModalPerfilUsuario
        :is-open="showProfileModal"
        @close="showProfileModal = false"
    />
  </div>
</template>
