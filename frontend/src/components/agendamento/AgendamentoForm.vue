<script lang="ts" setup>
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Textarea} from '@/components/ui/textarea'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {
  TipoAgendamento,
  TipoConsultaEnum,
  TipoProcedimentoEnum
} from "@/types/agendamentoTypes.ts";
import {LABELS_CONSULTA, LABELS_PROCEDIMENTO} from "@/constants/agendaConstants.ts";
import {PrescricaoMedica} from "@/types/prescricaoTypes.ts";
import {Checkbox} from "@/components/ui/checkbox";

export type PrescricaoComLabel = PrescricaoMedica & { labelFormatado: string };

defineProps<{
  tipo: TipoAgendamento
  horario: string
  dataSelecionada?: string
  diaCiclo: number | null
  observacoes: string
  horarioAbertura: string
  horarioFechamento: string
  prescricoesDisponiveis: PrescricaoComLabel[]
  prescricaoSelecionadaId: string
  diasPermitidos: number[]
  tipoConsulta: TipoConsultaEnum | ''
  tipoProcedimento: TipoProcedimentoEnum | ''
  encaixe: boolean
}>()

const emit = defineEmits<{
  (e: 'update:tipo', value: TipoAgendamento): void
  (e: 'update:horario', value: string): void
  (e: 'update:diaCiclo', value: number): void
  (e: 'update:prescricaoSelecionadaId', value: string): void
  (e: 'update:observacoes', value: string): void
  (e: 'update:tipoConsulta', value: string): void
  (e: 'update:tipoProcedimento', value: string): void
  (e: 'update:encaixe', value: boolean): void
  (e: 'confirmar'): void
}>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Agendamento</CardTitle>
    </CardHeader>
    <CardContent class="space-y-5">
      <div>
        <Label>Tipo de Agendamento</Label>
        <Select
            :model-value="tipo"
            @update:model-value="(val) => emit('update:tipo', val as TipoAgendamento)"
        >
          <SelectTrigger class="w-full">
            <SelectValue placeholder="Selecione o tipo..."/>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="infusao">Infusão</SelectItem>
            <SelectItem value="consulta">Consulta</SelectItem>
            <SelectItem value="procedimento">Procedimento</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div v-if="tipo === 'infusao'" class="space-y-4">
        <div>
          <Label>Prescrição</Label>
          <Select
              :model-value="prescricaoSelecionadaId"
              @update:model-value="(val) => emit('update:prescricaoSelecionadaId', val as string)"
          >
            <SelectTrigger>
              <SelectValue placeholder="Selecione a prescrição"/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="p in prescricoesDisponiveis" :key="p.id" :value="p.id">
                {{ p.labelFormatado }}
              </SelectItem>
            </SelectContent>
          </Select>
          <p v-if="prescricoesDisponiveis.length === 0" class="text-xs text-red-500 mt-1">
            Nenhuma prescrição ativa encontrada para este paciente.
          </p>
        </div>

        <div v-if="prescricaoSelecionadaId">
          <Label>Dia do Ciclo</Label>

          <div v-if="diasPermitidos.length > 0">
            <Select
                :model-value="diaCiclo?.toString()"
                @update:model-value="(val) => emit('update:diaCiclo', parseInt(val as string))"
            >
              <SelectTrigger>
                <SelectValue placeholder="Selecione o dia"/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="dia in diasPermitidos" :key="dia" :value="dia.toString()">
                  Dia {{ dia }}
                </SelectItem>
              </SelectContent>
            </Select>
            <p class="text-xs text-gray-500 mt-1">
              Dias disponíveis para agendamento neste ciclo.
            </p>
          </div>

          <div v-else class="px-3 py-2 bg-amber-50 border border-amber-100 rounded text-sm text-amber-950">
            Todos os dias deste ciclo já foram agendados.
          </div>
        </div>
      </div>

      <div v-if="tipo === 'consulta'" class="space-y-4">
        <div>
          <Label>Tipo de Consulta</Label>
          <Select
              :model-value="tipoConsulta"
              @update:model-value="(val) => emit('update:tipoConsulta', val as string)"
          >
            <SelectTrigger>
              <SelectValue placeholder="Selecione..."/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="opt in LABELS_CONSULTA" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div v-if="tipo === 'procedimento'" class="space-y-4">
        <div>
          <Label>Tipo de Procedimento</Label>
          <Select
              :model-value="tipoProcedimento"
              @update:model-value="(val) => emit('update:tipoProcedimento', val as string)"
          >
            <SelectTrigger>
              <SelectValue placeholder="Selecione..."/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="opt in LABELS_PROCEDIMENTO" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div v-if="dataSelecionada" class="space-y-5">
        <div>
          <Label>Horário</Label>
          <Input :model-value="horario" type="time" @update:model-value="(val) => emit('update:horario', String(val))"/>
          <p class="text-xs text-gray-500 mt-1">
            Funcionamento: {{ horarioAbertura }} às {{ horarioFechamento }}
          </p>
        </div>

        <div class="flex items-center space-x-2 py-2">
          <Checkbox
              id="encaixe"
              :checked="encaixe"
              @update:checked="(val) => emit('update:encaixe', val === true)"
          />
          <Label class="cursor-pointer" for="encaixe">Encaixe</Label>
        </div>

        <div>
          <Label>Observações</Label>
          <Textarea :model-value="observacoes"
                    @update:model-value="(val) => emit('update:observacoes', String(val))"/>
        </div>

        <Button
            :disabled="
            (tipo === 'infusao' && (!prescricaoSelecionadaId || diasPermitidos.length === 0)) ||
            (tipo === 'consulta' && !tipoConsulta) ||
            (tipo === 'procedimento' && !tipoProcedimento)
          "
            class="w-full"
            @click="emit('confirmar')"
        >
          Confirmar Agendamento
        </Button>
      </div>
    </CardContent>
  </Card>
</template>
