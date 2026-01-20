<script lang="ts" setup>
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

defineProps<{
  items: any[]
}>()

const containerRef = ref<HTMLElement | null>(null)

const scroll = (direction: 'left' | 'right') => {
  if (!containerRef.value) return
  const amount = 200
  containerRef.value.scrollBy({
    left: direction === 'left' ? -amount : amount,
    behavior: 'smooth'
  })
}
</script>

<template>
  <div class="bg-gray-50 p-1 rounded-lg border flex items-center gap-1 mb-4 w-full">
    <Button
        class="h-8 w-8 shrink-0 text-gray-400 hover:text-gray-900"
        size="icon"
        variant="ghost"
        @click="scroll('left')"
    >
      <ChevronLeft class="h-4 w-4"/>
    </Button>

    <div
        ref="containerRef"
        class="flex items-center gap-2 overflow-x-auto flex-1 px-1 w-0"
        style="scrollbar-width: thin; -ms-overflow-style: -ms-autohiding-scrollbar;"
    >
      <template v-for="(item, index) in items" :key="index">
        <slot name="item" :item="item" :index="index"></slot>
      </template>
    </div>

    <Button
        class="h-8 w-8 shrink-0 text-gray-400 hover:text-gray-900"
        size="icon"
        variant="ghost"
        @click="scroll('right')"
    >
      <ChevronRight class="h-4 w-4"/>
    </Button>

    <div v-if="$slots.actions" class="flex items-center pl-1">
      <div class="w-px h-5 bg-gray-300 mx-1 shrink-0"></div>
      <slot name="actions"></slot>
    </div>
  </div>
</template>
