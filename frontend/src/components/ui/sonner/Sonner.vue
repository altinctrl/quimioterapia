<script setup lang="ts">
import { Toaster as Sonner, type ToasterProps } from 'vue-sonner'
import {
  CheckCircle,
  Info,
  Loader2,
  XCircle,
  AlertTriangle,
  X
} from 'lucide-vue-next'

const props = defineProps<ToasterProps>()
</script>

<template>
  <Sonner
    class="toaster group"
    v-bind="props"
    :duration="10000"
    :icons="{
      success: CheckCircle,
      info: Info,
      warning: AlertTriangle,
      error: XCircle,
      loading: Loader2,
      close: X,
    }"
    :toast-options="{
      classes: {
        toast: 'group toast group-[.toaster]:bg-background group-[.toaster]:text-foreground group-[.toaster]:border-border group-[.toaster]:shadow-lg',
        description: 'group-[.toast]:text-muted-foreground',
        actionButton: 'group-[.toast]:bg-primary group-[.toast]:text-primary-foreground',
        cancelButton: 'group-[.toast]:bg-muted group-[.toast]:text-muted-foreground',
      },
    }"
  />
</template>
