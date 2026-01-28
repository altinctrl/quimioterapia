import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '@/stores/storeAuth.ts'
import ViewLogin from '@/views/ViewLogin.vue'
import Layout from '@/components/Layout.vue'
import ViewPacientes from '@/views/ViewPacientes.vue'
import ViewProntuario from "@/views/ViewProntuario.vue";
import ViewAgenda from '@/views/ViewAgenda.vue'
import ViewAgendamento from '@/views/ViewAgendamento.vue'
import ViewFarmacia from '@/views/ViewFarmacia.vue'
import ViewRelatorios from '@/views/ViewRelatorios.vue'
import ViewProtocolos from '@/views/ViewProtocolos.vue'
import ViewAjustes from '@/views/ViewAjustes.vue'
import ViewPrescricao from '@/views/ViewPrescricao.vue'
import ViewEquipe from '@/views/ViewEquipe.vue';

const router = createRouter({
  history: createWebHistory(), routes: [
    {path: '/login', name: 'Login', component: ViewLogin},
    {path: '/', component: Layout, meta: {requiresAuth: true},
      children: [{path: '', redirect: '/agenda'},
        {path: 'pacientes', name: 'Pacientes', component: ViewPacientes },
        {path: 'pacientes/:id', name: 'Prontuario', component: ViewProntuario},
        {path: 'agenda', name: 'Agenda', component: ViewAgenda},
        {path: 'agendamento', name: 'Agendamento', component: ViewAgendamento},
        {path: 'farmacia', name: 'Farmacia', component: ViewFarmacia},
        {path: 'relatorios', name: 'Relatorios', component: ViewRelatorios},
        {path: 'protocolos/novo', name: 'NovoProtocolo', component: ViewProtocolos},
        {path: 'protocolos/:id', name: 'EditarProtocolo', component: ViewProtocolos},
        {path: 'ajustes', name: 'Ajustes', component: ViewAjustes},
        {path: 'prescricao', name: 'Prescricao', component: ViewPrescricao},
        {path: 'equipe', name: 'Equipe', component: ViewEquipe}
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
