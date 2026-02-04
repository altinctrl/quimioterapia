<script lang="ts" setup>
import {computed} from 'vue'

export interface TimelineItem {
  id?: string
  data: string
  titulo: string
  descricao?: string
  usuario?: string
  meta?: string
}

const props = defineProps<{
  itens: TimelineItem[]
  vazioTexto?: string
}>()

const itensOrdenados = computed(() => {
  if (!props.itens) return []
  return [...props.itens].sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime())
})

const formatarDataHora = (data: string) => {
  if (!data) return '-'
  const dt = new Date(data)
  return `${dt.toLocaleDateString('pt-BR')} ${dt.toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'})}`
}
</script>

<template>
  <div class="space-y-4">
    <div v-if="itensOrdenados.length === 0" class="text-sm text-gray-500 italic">
      {{ vazioTexto || 'Nenhum histórico disponível.' }}
    </div>

    <ol v-else class="relative border-l border-gray-200 pl-4 space-y-4">
      <li v-for="(item, index) in itensOrdenados" :key="item.id || index" class="ml-2">
        <span class="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full bg-blue-600"></span>
        <div class="flex flex-col gap-1">
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span class="font-medium text-gray-700">{{ formatarDataHora(item.data) }}</span>
            <span v-if="item.usuario" class="text-gray-400">•</span>
            <span v-if="item.usuario" class="text-gray-600">{{ item.usuario }}</span>
            <span v-if="item.meta" class="text-gray-400">•</span>
            <span v-if="item.meta" class="text-gray-500">{{ item.meta }}</span>
          </div>
          <div class="text-sm font-semibold text-gray-900">{{ item.titulo }}</div>
          <div v-if="item.descricao" class="text-sm text-gray-600">
            {{ item.descricao }}
          </div>
        </div>
      </li>
    </ol>
  </div>
</template>
