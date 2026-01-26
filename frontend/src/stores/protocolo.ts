import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import {Protocolo} from "@/types/protocoloTypes.ts";

export const useProtocoloStore = defineStore('protocolo', () => {
  const protocolos = ref<Protocolo[]>([])

  function getProtocoloById(id: string) {
    return protocolos.value.find(p => p.id === id)
  }

  async function fetchProtocolos(ativo: boolean = true) {
    try {
      const res = await api.get('/api/protocolos', {params: {ativo}})
      protocolos.value = res.data
    } catch (e) {
      console.error(e)
    }
  }

  async function adicionarProtocolo(protocolo: Partial<Protocolo>) {
    try {
      const res = await api.post('/api/protocolos', protocolo)
      protocolos.value.push(res.data)
    } catch (e) {
      toast.error("Erro ao salvar protocolo")
      throw e
    }
  }

  async function importarProtocolos(lista: Partial<Protocolo>[]) {
    try {
      const res = await api.post('/api/protocolos', lista)
      protocolos.value.push(...res.data)
    } catch (e) {
      toast.error("Erro na importação.")
      throw e
    }
  }

  async function atualizarProtocolo(id: string, dados: Partial<Protocolo>) {
    try {
      const res = await api.put(`/api/protocolos/${id}`, dados)
      const idx = protocolos.value.findIndex(p => p.id === id)
      if (idx !== -1) protocolos.value[idx] = res.data
    } catch (e) {
      toast.error("Erro ao atualizar protocolo")
      throw e
    }
  }

  async function desativarProtocolo(id: string) {
    try {
      await api.delete(`/api/protocolos/${id}`)
      const idx = protocolos.value.findIndex(p => p.id === id)
      if (idx !== -1) protocolos.value[idx].ativo = false
    } catch (e) {
      toast.error("Erro ao desativar")
      throw e
    }
  }

  return {
    protocolos,
    getProtocoloById,
    fetchProtocolos,
    adicionarProtocolo,
    importarProtocolos,
    atualizarProtocolo,
    desativarProtocolo
  }
})
