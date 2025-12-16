import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '@/stores/auth'
import Login from '@/components/Login.vue'
import Layout from '@/components/Layout.vue'
import Dashboard from '@/components/Dashboard.vue'
import Pacientes from '@/components/Pacientes.vue'
import Agenda from '@/components/Agenda.vue'
import Agendamento from '@/components/Agendamento.vue'
import Farmacia from '@/components/Farmacia.vue'
import Relatorios from '@/components/Relatorios.vue'
import Protocolos from '@/components/Protocolos.vue'
import Ajustes from '@/components/Ajustes.vue'
import PrescricaoMedica from '@/components/PrescricaoMedica.vue'

const router = createRouter({
  history: createWebHistory(), routes: [{
    path: '/login', name: 'Login', component: Login
  }, {
    path: '/', component: Layout, meta: {requiresAuth: true}, children: [{path: '', redirect: '/dashboard'}, {
      path: 'dashboard', name: 'Dashboard', component: Dashboard
    }, {path: 'pacientes', name: 'Pacientes', component: Pacientes}, {
      path: 'agenda', name: 'Agenda', component: Agenda
    }, {path: 'agendamento', name: 'Agendamento', component: Agendamento}, {
      path: 'farmacia', name: 'Farmacia', component: Farmacia
    }, {path: 'relatorios', name: 'Relatorios', component: Relatorios}, {
      path: 'protocolos', name: 'Protocolos', component: Protocolos
    }, {path: 'ajustes', name: 'Ajustes', component: Ajustes}, {
      path: 'prescricao', name: 'Prescricao', component: PrescricaoMedica
    }]
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
