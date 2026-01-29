import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/services/api'
import {toast} from 'vue-sonner'
import {Protocolo} from "@/types/typesProtocolo.ts";

export const useProtocoloStore = defineStore('protocolo', () => {
  const protocolos = ref<Protocolo[]>([])

  function getProtocoloById(id: string) {
    return protocolos.value.find(p => p.id === id)
  }

  async function fetchProtocolos(ativo?: boolean) {
    try {
      const params = ativo !== undefined ? { ativo } : {};
      const res = await api.get('/api/protocolos', {params})
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

  async function excluirProtocolo(id: string) {
    try {
      await api.delete(`/api/protocolos/${id}`)
      await fetchProtocolos()
    } catch (e) {
      toast.error("Erro ao excluir")
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
    excluirProtocolo,
  }
})
