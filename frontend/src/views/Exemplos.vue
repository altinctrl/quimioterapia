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
    <Card>
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
          <Button type="submit" variant="primary">Enviar</Button>
        </div>
      </Form>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Form, Field, ErrorMessage } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import api from '../services/api';

const validationSchema = toTypedSchema(
  z.object({
    name: z.string().nonempty('O nome é obrigatório'),
    email: z.string().nonempty('O e-mail é obrigatório').email('O e-mail é inválido'),
    message: z.string().nonempty('A mensagem é obrigatória').min(10, 'A mensagem deve ter no mínimo 10 caracteres'),
  })
);

function onSubmit(values: any) {
  alert(JSON.stringify(values, null, 2));
}


</script>
