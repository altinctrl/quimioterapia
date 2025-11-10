<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Exemplos de Componentes e Layout</h1>

    <!-- Grid System Explanation Card -->
    <Card class="mb-6">
      <template #header>
        <h2 class="text-xl font-semibold">Sistema de Grid Responsivo (12 Colunas)</h2>
      </template>
      <p>O layout utiliza um sistema de grid de 12 colunas, similar ao Bootstrap. Use as classes `grid`, `grid-cols-12`, e `col-span-*` para criar layouts. As classes são responsivas, permitindo que você defina diferentes larguras para diferentes tamanhos de tela (ex: `md:col-span-6`).</p>
    </Card>

    <!-- Grid System Example Cards -->
    <div class="grid grid-cols-12 gap-6 mb-6">
      <div class="col-span-12 md:col-span-4">
        <Card>
          <template #header><code>.col-span-4</code></template>
          <p>Este card ocupa 4 das 12 colunas em telas médias e maiores.</p>
        </Card>
      </div>
      <div class="col-span-12 md:col-span-8">
        <Card>
          <template #header><code>.col-span-8</code></template>
          <p>Este card ocupa 8 das 12 colunas em telas médias e maiores.</p>
        </Card>
      </div>
      <div class="col-span-12 md:col-span-6">
        <Card>
          <template #header><code>.col-span-6</code></template>
          <p>Este card ocupa 6 das 12 colunas em telas médias e maiores.</p>
        </Card>
      </div>
      <div class="col-span-12 md:col-span-6">
        <Card>
          <template #header><code>.col-span-6</code></template>
          <p>Este card ocupa 6 das 12 colunas em telas médias e maiores.</p>
        </Card>
      </div>
    </div>

    <!-- Form Example -->
    <Card class="mb-6">
      <template #header>
        <h2 class="text-xl font-semibold">Exemplo de Formulário com Validação</h2>
      </template>
      <Form @submit="onSubmit" :validation-schema="validationSchema">
        <div class="grid grid-cols-12 gap-6">
          <div class="col-span-12 md:col-span-6">
            <div class="form-group">
              <label for="name" class="form-label">Nome Completo</label>
              <Field name="name" type="text" id="name" class="form-control" placeholder="Digite seu nome" validate-on-input />
              <ErrorMessage name="name" class="text-red-500 text-sm mt-1" />
            </div>
          </div>
          <div class="col-span-12 md:col-span-6">
            <div class="form-group">
              <label for="email" class="form-label">Endereço de E-mail</label>
              <Field name="email" type="email" id="email" class="form-control" placeholder="seu@email.com" validate-on-input />
              <ErrorMessage name="email" class="text-red-500 text-sm mt-1" />
            </div>
          </div>
          <div class="col-span-12">
            <div class="form-group">
              <label for="message" class="form-label">Mensagem</label>
              <Field as="textarea" name="message" id="message" rows="4" class="form-control" placeholder="Deixe sua mensagem..." validate-on-input />
              <ErrorMessage name="message" class="text-red-500 text-sm mt-1" />
            </div>
          </div>
        </div>
        <div class="flex justify-end space-x-4 mt-4">
          <Button type="button" variant="default">Cancelar</Button>
          <Button type="submit" variant="primary" :loading="isSubmitting">Enviar</Button>
        </div>
      </Form>
    </Card>

    <!-- Other Components Example -->
    <Card>
      <template #header>
        <h2 class="text-xl font-semibold">Outros Componentes</h2>
      </template>
      <div class="flex flex-wrap gap-4">
        <!-- Toast Buttons -->
        <Button @click="showSuccessToast">Toast Sucesso</Button>
        <Button @click="showErrorToast" variant="danger">Toast Erro</Button>
        <Button @click="showInfoToast" variant="info">Toast Info</Button>
        <Button @click="showWarningToast" variant="warning">Toast Aviso</Button>
        
        <!-- Loading Button -->
        <Button @click="showLoadingButton" :loading="isLoadingButton">
          <template #icon>
            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </template>
          Botão com Ícone
        </Button>

        <!-- Modal Button -->
        <Button @click="showModal = true" variant="secondary">Abrir Modal</Button>
      </div>
    </Card>

    <!-- Modal Component -->
    <Modal :show="showModal" @close="showModal = false">
      <template #header>
        Título do Modal
      </template>
      
      <p>Este é o conteúdo do modal. Você pode colocar qualquer coisa aqui, como texto, imagens, ou até mesmo um formulário.</p>
      
      <template #footer>
        <Button @click="showModal = false" variant="default">Cancelar</Button>
        <Button @click="handleModalConfirm" variant="primary">Confirmar</Button>
      </template>
    </Modal>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Form, Field, ErrorMessage } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import { useToast } from 'vue-toastification';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import Modal from '../components/Modal.vue';
import api from '../services/api';

const toast = useToast();
const isSubmitting = ref(false);
const isLoadingButton = ref(false);
const showModal = ref(false);

const validationSchema = toTypedSchema(
  z.object({
    name: z.string().nonempty('O nome é obrigatório'),
    email: z.string().nonempty('O e-mail é obrigatório').email('O e-mail é inválido'),
    message: z.string().nonempty('A mensagem é obrigatória').min(10, 'A mensagem deve ter no mínimo 10 caracteres'),
  })
);

function onSubmit(values: any) {
  isSubmitting.value = true;
  setTimeout(() => {
    isSubmitting.value = false;
    toast.success('Formulário enviado com sucesso!');
    console.log(JSON.stringify(values, null, 2));
  }, 2000);
}

function showSuccessToast() {
  toast.success('Esta é uma notificação de sucesso!');
}

function showErrorToast() {
  toast.error('Esta é uma notificação de erro!');
}

function showInfoToast() {
  toast.info('Esta é uma notificação de informação.');
}

function showWarningToast() {
  toast.warning('Esta é uma notificação de aviso.');
}

function showLoadingButton() {
  isLoadingButton.value = true;
  setTimeout(() => {
    isLoadingButton.value = false;
  }, 2000);
}

function handleModalConfirm() {
  toast.info('Ação do modal confirmada!');
  showModal.value = false;
}
</script>
