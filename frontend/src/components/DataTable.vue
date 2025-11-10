<template>
  <div class="w-full overflow-x-auto rounded-lg shadow-xs">
    <table class="w-full whitespace-no-wrap">
      <thead>
        <tr class="text-xs font-semibold tracking-wider text-left text-gray-500 uppercase border-b border-gray-200 bg-gray-50">
          <th v-for="header in headers" :key="header.value" class="px-4 py-2">{{ header.text }}</th>
          <th v-if="$slots.actions" class="px-4 py-2">Ações</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-100">
        <tr v-for="item in items" :key="item.id" class="text-gray-700 hover:bg-gray-100">
          <td v-for="header in headers" :key="header.value" class="px-4 py-3 text-sm">
            {{ item[header.value] }}
          </td>
          <td v-if="$slots.actions" class="px-4 py-3 text-sm">
            <slot name="actions" :item="item"></slot>
          </td>
        </tr>
        <tr v-if="items.length === 0">
          <td :colspan="headers.length + ($slots.actions ? 1 : 0)" class="px-6 py-4 text-center text-gray-500">
            Nenhum dado encontrado.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">


interface Header {
  text: string;
  value: string;
}

interface Item {
  id: number | string;
  [key: string]: any;
}

defineProps({
  headers: {
    type: Array as () => Header[],
    required: true,
  },
  items: {
    type: Array as () => Item[],
    required: true,
  },
});
</script>