<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Lista de Pacientes</h1>
    <Card class="mb-6">
      <div class="mb-6 flex items-center space-x-4">
        <div class="form-group flex-1">
          <label for="pacienteCodigoInput" class="form-label">Buscar Paciente por Código</label>
          <div class="flex items-center space-x-2">
            <input id="pacienteCodigoInput" v-model="pacienteCodigoInput" type="number" placeholder="Digite o código do paciente" class="form-control">
            <Button @click="fetchPacientePorCodigo" :disabled="loadingPaciente" variant="success" class="whitespace-nowrap">
              <span v-if="loadingPaciente">Buscando...</span>
              <span v-else>Buscar</span>
            </Button>
          </div>
        </div>
      </div>
    </Card>

    <Card v-if="pacienteDetalhe" class="mt-6">
      <template #header>
        <h2 class="text-lg font-semibold">Detalhes do Paciente</h2>
      </template>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div><span class="font-medium">Código:</span> {{ pacienteDetalhe.codigo }}</div>
        <div><span class="font-medium">Nome:</span> {{ pacienteDetalhe.nome }}</div>
        <div><span class="font-medium">Data de Nascimento:</span> {{ pacienteDetalhe.dt_nascimento }}</div>
        <div><span class="font-medium">Nome da Mãe:</span> {{ pacienteDetalhe.nome_mae }}</div>
        <div><span class="font-medium">Sexo:</span> {{ pacienteDetalhe.sexo }}</div>
        <div><span class="font-medium">Cor:</span> {{ pacienteDetalhe.cor }}</div>
        <div v-if="pacienteDetalhe.nome_pai"><span class="font-medium">Nome do Pai:</span> {{ pacienteDetalhe.nome_pai }}</div>
      </div>
    </Card>

    <Card class="mt-6">
      <DataTable :headers="headers" :items="pacientes">
        <template #actions="{ item }">
          <div class="flex space-x-2">
            <Button @click="viewPaciente(item)" variant="info" size="sm">
              <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </Button>
            <Button @click="editPaciente(item)" variant="warning" size="sm">
              <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L15.232 5.232z" />
              </svg>
            </Button>
            <Button @click="deletePaciente(item)" variant="danger" size="sm">
              <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-4v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </Button>
          </div>
        </template>
      </DataTable>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import api from '../services/api';
import Card from '../components/Card.vue';
import DataTable from '../components/DataTable.vue';
import Button from '../components/Button.vue';

const toast = useToast();

const pacienteCodigoInput = ref(null);
const loadingPaciente = ref(false);
const pacienteDetalhe = ref<any | null>(null);

const headers = ref([
  { text: 'Prontuário', value: 'codigo' },
  { text: 'Nome', value: 'nome' },
  { text: 'Data de Nascimento', value: 'dt_nascimento' },
  { text: 'Nome da Mãe', value: 'nome_mae' },
]);

const pacientes = ref([]);

onMounted(async () => {
  try {
    const { data } = await api.get('/api/pacientes');
    pacientes.value = data;
  } catch (error) {
    toast.error('Falha ao carregar a lista de pacientes.');
  }
});

const fetchPacientePorCodigo = async () => {
  if (!pacienteCodigoInput.value) {
    toast.error('Por favor, digite um código.');
    return;
  }
  loadingPaciente.value = true;
  pacienteDetalhe.value = null; // Clear previous details
  try {
    const { data } = await api.get(`/api/pacientes/${pacienteCodigoInput.value}`);
    pacienteDetalhe.value = data;
    toast.success(`Paciente encontrado: ${data.nome}`);
  } catch (error) {
    toast.error('Paciente não encontrado.');
  } finally {
    loadingPaciente.value = false;
  }
};

const viewPaciente = (item: any) => {
  toast.info(`Visualizando paciente: ${item.nome}`);
};

const editPaciente = (item: any) => {
  toast.warning(`Editando paciente: ${item.nome}`);
};

const deletePaciente = (item: any) => {
  toast.error(`Deletando paciente: ${item.nome}`);
};
</script>
