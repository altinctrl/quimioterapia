import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import Layout from '@/components/Layout.vue'
import PacientesView from '@/views/PacientesView.vue'
import AgendaView from '@/views/AgendaView.vue'
import Agendamento from '@/components/Agendamento.vue'
import Farmacia from '@/components/Farmacia.vue'
import RelatoriosView from '@/views/RelatoriosView.vue'
import ProtocolosView from '@/views/ProtocolosView.vue'
import Ajustes from '@/components/Ajustes.vue'
import PrescricaoView from '@/views/PrescricaoView.vue'

const router = createRouter({
  history: createWebHistory(), routes: [
    {path: '/login', name: 'Login', component: LoginView},
    {path: '/', component: Layout, meta: {requiresAuth: true},
      children: [{path: '', redirect: '/agenda'},
        {path: 'pacientes', name: 'Pacientes', component: PacientesView },
        {path: 'agenda', name: 'Agenda', component: AgendaView},
        {path: 'agendamento', name: 'Agendamento', component: Agendamento},
        {path: 'farmacia', name: 'Farmacia', component: Farmacia},
        {path: 'relatorios', name: 'Relatorios', component: RelatoriosView},
        {path: 'protocolos', name: 'Protocolos', component: ProtocolosView},
        {path: 'ajustes', name: 'Ajustes', component: Ajustes},
        {path: 'prescricao', name: 'Prescricao', component: PrescricaoView}
      ]
    }]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
