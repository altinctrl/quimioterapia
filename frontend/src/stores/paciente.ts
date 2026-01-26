import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import {Paciente} from "@/types/pacienteTypes.ts";

export const usePacienteStore = defineStore('paciente', () => {
  const pacientes = ref<Paciente[]>([])
  const totalPacientes = ref(0)
  const resultadosBusca = ref<Paciente[]>([])

  function getPacienteById(id: string) {
    const p = pacientes.value.find(p => p.id === id)
    if (p && !p.idade && p.dataNascimento) {
      const nascimento = new Date(p.dataNascimento)
      const hoje = new Date()
      let idade = hoje.getFullYear() - nascimento.getFullYear()
      const m = hoje.getMonth() - nascimento.getMonth()
      if (m < 0 || (m === 0 && hoje.getDate() < nascimento.getDate())) {
        idade--
      }
      p.idade = idade
    }
    return p
  }

  async function fetchPacientes(page = 1, size = 10, termo = '', ordenacao = 'recentes') {
    try {
      const params: any = {page, size, ordenacao}
      if (termo) params.termo = termo

      const res = await api.get('/api/pacientes', {params})

      pacientes.value = res.data.items
      totalPacientes.value = res.data.total
    } catch (e) {
      console.error(e)
    }
  }

  async function carregarPaciente(id: string) {
    let p = getPacienteById(id)
    if (p) return p

    try {
      const pacienteEncontrado = (await api.get(`/api/pacientes/${id}`)).data

      if (pacienteEncontrado) {
        const existe = pacientes.value.some(x => x.id == pacienteEncontrado.id)
        if (!existe) pacientes.value.push(pacienteEncontrado)
        return pacienteEncontrado
      }
    } catch (e) {
      console.error("Erro ao carregar paciente.", e)
      return null
    }
  }

  async function buscarPacientesDropdown(termo: string) {
    if (!termo || termo.length < 2) {
      resultadosBusca.value = []
      return
    }
    try {
      const res = await api.get('/api/pacientes', {params: {termo, page: 1, size: 20}})
      resultadosBusca.value = res.data.items
    } catch (e) {
      console.error(e)
    }
  }

  async function adicionarPaciente(paciente: any) {
    try {
      const res = await api.post('/api/pacientes', paciente)
      pacientes.value.push(res.data)
      return res.data
    } catch (e) {
      throw e
    }
  }

  async function atualizarPaciente(id: string, dados: any) {
    try {
      const res = await api.put(`/api/pacientes/${id}`, dados)
      const idx = pacientes.value.findIndex(p => p.id === id)
      if (idx !== -1) pacientes.value[idx] = res.data
    } catch (e) {
      toast.error("Erro ao atualizar paciente")
    }
  }

  return {
    pacientes,
    totalPacientes,
    resultadosBusca,
    getPacienteById,
    fetchPacientes,
    carregarPaciente,
    buscarPacientesDropdown,
    adicionarPaciente,
    atualizarPaciente
  }
})