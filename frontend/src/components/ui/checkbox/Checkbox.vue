<script lang="ts" setup>
import {CheckboxIndicator, CheckboxRoot} from "radix-vue"
import {Check} from "lucide-vue-next"
import {cn} from "@/lib/utils"

const checked = defineModel<boolean>('checked')

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <CheckboxRoot
      v-model:checked="checked"
      :class="
      cn('grid place-content-center peer h-4 w-4 shrink-0 rounded-sm border border-primary shadow focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground',
         props.class)"
      v-bind="$attrs"
  >
    <CheckboxIndicator class="grid place-content-center text-current">
      <Check class="h-4 w-4"/>
    </CheckboxIndicator>
  </CheckboxRoot>
</template>