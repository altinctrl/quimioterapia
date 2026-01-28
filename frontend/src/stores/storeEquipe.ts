import {defineStore} from 'pinia'
import api from '@/services/api'
import {AusenciaProfissional, EscalaPlantao, Profissional} from "@/types/typesEquipe.ts";

export const useEquipeStore = defineStore('equipe', {
  state: () => ({
    profissionais: [] as Profissional[],
    escalaDia: [] as EscalaPlantao[],
    ausencias: [] as AusenciaProfissional[],
    isLoading: false,
    error: null as string | null
  }),

  actions: {
    async fetchProfissionais(apenasAtivos = true) {
      this.isLoading = true
      try {
        const {data} = await api.get('/api/equipe/profissionais', {params: {apenas_ativos: apenasAtivos}})
        this.profissionais = data
      } catch (err: any) {
        this.error = 'Erro ao buscar profissionais'
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },

    async criarProfissional(payload: Partial<Profissional>) {
      try {
        const {data} = await api.post('/api/equipe/profissionais', payload)
        this.profissionais.push(data)
        return data
      } catch (err: any) {
        throw new Error(err.response?.data?.detail || 'Erro ao criar profissional')
      }
    },

    async atualizarProfissional(username: string, payload: Partial<Profissional>) {
      try {
        const {data} = await api.put(`/api/equipe/profissionais/${username}`, payload)
        const index = this.profissionais.findIndex(p => p.username === username)
        if (index !== -1) this.profissionais[index] = data
        return data
      } catch (err: any) {
        throw new Error(err.response?.data?.detail || 'Erro ao atualizar profissional')
      }
    },

    async fetchEscalaDia(dataIso: string) {
      this.isLoading = true
      try {
        const {data} = await api.get(`/api/equipe/escala/${dataIso}`)
        this.escalaDia = data
      } catch (err: any) {
        this.error = 'Erro ao buscar escala'
      } finally {
        this.isLoading = false
      }
    },

    async adicionarEscala(payload: Partial<EscalaPlantao>) {
      try {
        const {data} = await api.post('/api/equipe/escala', payload)
        this.escalaDia.push(data)
        return data
      } catch (err: any) {
        throw new Error(err.response?.data?.detail || 'Erro ao adicionar à escala')
      }
    },

    async removerEscala(itemId: string) {
      try {
        await api.delete(`/api/equipe/escala/${itemId}`)
        this.escalaDia = this.escalaDia.filter(e => e.id !== itemId)
      } catch (err: any) {
        throw new Error('Erro ao remover da escala')
      }
    },

    async fetchAusencias(start: string, end: string) {
      this.isLoading = true
      try {
        const {data} = await api.get('/api/equipe/ausencias', {params: {start, end}})
        this.ausencias = data
      } catch (err: any) {
        this.error = 'Erro ao buscar ausências'
      } finally {
        this.isLoading = false
      }
    },

    async registrarAusencia(payload: Partial<AusenciaProfissional>) {
      try {
        const {data} = await api.post('/api/equipe/ausencias', payload)
        this.ausencias.push(data)
        return data
      } catch (err: any) {
        throw new Error(err.response?.data?.detail || 'Erro ao registrar ausência')
      }
    },

    async removerAusencia(id: string) {
      try {
        await api.delete(`/api/equipe/ausencias/${id}`)
        this.ausencias = this.ausencias.filter(a => a.id !== id)
      } catch (err: any) {
        throw new Error('Erro ao remover ausência')
      }
    }
  }
})
