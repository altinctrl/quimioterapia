import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import Layout from '@/components/Layout.vue'
import PacientesView from '@/views/PacientesView.vue'
import AgendaView from '@/views/AgendaView.vue'
import AgendamentoView from '@/views/AgendamentoView.vue'
import FarmaciaView from '@/views/FarmaciaView.vue'
import RelatoriosView from '@/views/RelatoriosView.vue'
import ProtocolosView from '@/views/ProtocolosView.vue'
import AjustesView from '@/views/AjustesView.vue'
import PrescricaoView from '@/views/PrescricaoView.vue'
import EquipeView from '@/views/EquipeView.vue';

const router = createRouter({
  history: createWebHistory(), routes: [
    {path: '/login', name: 'Login', component: LoginView},
    {path: '/', component: Layout, meta: {requiresAuth: true},
      children: [{path: '', redirect: '/agenda'},
        {path: 'pacientes', name: 'Pacientes', component: PacientesView },
        {path: 'agenda', name: 'Agenda', component: AgendaView},
        {path: 'agendamento', name: 'Agendamento', component: AgendamentoView},
        {path: 'farmacia', name: 'Farmacia', component: FarmaciaView},
        {path: 'relatorios', name: 'Relatorios', component: RelatoriosView},
        {path: 'protocolos', name: 'Protocolos', component: ProtocolosView},
        {path: 'ajustes', name: 'Ajustes', component: AjustesView},
        {path: 'prescricao', name: 'Prescricao', component: PrescricaoView},
        {path: 'equipe', name: 'Equipe', component: EquipeView}
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
