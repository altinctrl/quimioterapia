import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '@/stores/auth'
import Login from '@/components/Login.vue'
import Layout from '@/components/Layout.vue'
import Dashboard from '@/components/Dashboard.vue'
import PacientesView from '@/views/PacientesView.vue'
import AgendaView from '@/views/AgendaView.vue'
import Agendamento from '@/components/Agendamento.vue'
import Farmacia from '@/components/Farmacia.vue'
import Relatorios from '@/components/Relatorios.vue'
import ProtocolosView from '@/views/ProtocolosView.vue'
import Ajustes from '@/components/Ajustes.vue'
import PrescricaoView from '@/views/PrescricaoView.vue'

const router = createRouter({
  history: createWebHistory(), routes: [
    {path: '/login', name: 'Login', component: Login},
    {path: '/', component: Layout, meta: {requiresAuth: true},
      children: [{path: '', redirect: '/dashboard'},
        {path: 'dashboard', name: 'Dashboard', component: Dashboard},
        {path: 'pacientes', name: 'Pacientes', component: PacientesView },
        {path: 'agenda', name: 'Agenda', component: AgendaView},
        {path: 'agendamento', name: 'Agendamento', component: Agendamento},
        {path: 'farmacia', name: 'Farmacia', component: Farmacia},
        {path: 'relatorios', name: 'Relatorios', component: Relatorios},
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
