<template>
  <Card>
    <template #header>
      <h1 class="text-xl font-semibold">Exemplos de API</h1>
    </template>

    <p class="mb-6">Esta página demonstra como o frontend pode interagir com a API para buscar dados, usando os padrões definidos no framework.</p>

    <div class="grid grid-cols-12 gap-6">
      
      <!-- Listar Pacientes -->
      <div class="p-4 border rounded-lg col-span-12 md:col-span-8">
        <h2 class="text-lg font-semibold mb-2">Listar Pacientes</h2>
        <p class="text-sm text-gray-600 mb-4">Clica no botão para buscar os primeiros 100 pacientes do banco de dados do AGHU.</p>
        <Button @click="fetchPacientes" :disabled="loadingPacientes" class="bg-blue-500 hover:bg-blue-600 text-white">
          <span v-if="loadingPacientes">Carregando...</span>
          <span v-else>Buscar Pacientes</span>
        </Button>
        <div v-if="errorPacientes" class="mt-4 p-2 bg-red-100 text-red-700 rounded text-sm">
          <strong>Erro:</strong> {{ errorPacientes }}
        </div>
        <div v-if="pacientes.length" class="mt-4">
          <h3 class="font-semibold">Resultados:</h3>
          <ul class="list-disc list-inside bg-gray-50 p-2 rounded mt-2 text-sm h-48 overflow-y-auto">
            <li v-for="paciente in pacientes" :key="paciente.pac_codigo">
              {{ paciente.nome }} (Cód: {{ paciente.pac_codigo }})
            </li>
          </ul>
        </div>
      </div>

      <!-- Obter Paciente por Código -->
      <div class="p-4 border rounded-lg col-span-12 md:col-span-4">
        <h2 class="text-lg font-semibold mb-2">Obter Paciente por Código</h2>
        <p class="text-sm text-gray-600 mb-4">Digite um código de paciente e clique em buscar.</p>
        <div class="flex items-center space-x-2">
          <input v-model="pacienteCodigoInput" type="number" placeholder="Digite o código do paciente" class="shadow-inner appearance-none border rounded w-full py-2 px-3 leading-tight focus:outline-none focus:shadow-outline">
          <Button @click="fetchPacientePorCodigo" :disabled="loadingPaciente" variant="success" class="whitespace-nowrap">
            <span v-if="loadingPaciente">Buscando...</span>
            <span v-else>Buscar por Código</span>
          </Button>
        </div>
        <div v-if="errorPaciente" class="mt-4 p-2 bg-red-100 text-red-700 rounded text-sm">
          <strong>Erro:</strong> {{ errorPaciente }}
        </div>
        <div v-if="pacienteDetalhe" class="mt-4">
          <h3 class="font-semibold">Detalhes do Paciente:</h3>
          <pre class="mt-2 text-sm bg-gray-100 p-2 rounded whitespace-pre-wrap">{{ JSON.stringify(pacienteDetalhe, null, 2) }}</pre>
        </div>
      </div>

    </div>
  </Card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import api from '../services/api';

// State for listing patients
const pacientes = ref<any[]>([]);
const loadingPacientes = ref(false);
const errorPacientes = ref('');

// State for getting a single patient
const pacienteCodigoInput = ref(null);
const pacienteDetalhe = ref<any | null>(null);
const loadingPaciente = ref(false);
const errorPaciente = ref('');

const fetchPacientes = async () => {
  loadingPacientes.value = true;
  errorPacientes.value = '';
  pacientes.value = [];
  try {
    const response = await api.get('/api/pacientes');
    pacientes.value = response.data;
  } catch (err: any) {
    errorPacientes.value = err.response?.data?.detail || err.message;
  } finally {
    loadingPacientes.value = false;
  }
};

const fetchPacientePorCodigo = async () => {
  if (!pacienteCodigoInput.value) {
    errorPaciente.value = 'Por favor, digite um código.';
    return;
  }
  loadingPaciente.value = true;
  errorPaciente.value = '';
  pacienteDetalhe.value = null;
  try {
    const response = await api.get(`/api/pacientes/${pacienteCodigoInput.value}`);
    pacienteDetalhe.value = response.data;
  } catch (err: any) {
    errorPaciente.value = err.response?.data?.detail || err.message;
  } finally {
    loadingPaciente.value = false;
  }
};
</script>