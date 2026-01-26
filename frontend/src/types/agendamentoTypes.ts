import {PrescricaoMedica} from "@/types/prescricaoTypes.ts";

import {Profissional} from "@/types/equipeTypes.ts";

export type Turno = 'manha' | 'tarde' | 'noite';

export enum AgendamentoStatusEnum {
  AGENDADO = 'agendado',
  AGUARDANDO_CONSULTA = 'aguardando-consulta',
  AGUARDANDO_EXAME = 'aguardando-exame',
  AGUARDANDO_MEDICAMENTO = 'aguardando-medicamento',
  INTERNADO = 'internado',
  SUSPENSO = 'suspenso',
  REMARCADO = 'remarcado',
  EM_TRIAGEM = 'em-triagem',
  EM_INFUSAO = 'em-infusao',
  INTERCORRENCIA = 'intercorrencia',
  CONCLUIDO = 'concluido'
}

export enum FarmaciaStatusEnum {
  AGUARDA_PRESCRICAO = 'aguarda-prescricao', // Não recebido
  VALIDANDO_PRESCRICAO = 'validando-prescricao', // Aguarda confirmação dos dados da prescrição
  PENDENTE = 'pendente',
  EM_PREPARACAO = 'em-preparacao',
  PRONTO = 'pronto',
  ENVIADO = 'enviado',
  MED_EM_FALTA = 'med-em-falta',
  MED_JUD_EM_FALTA = 'med-jud-em-falta',
  SEM_PROCESSO = 'sem-processo',
  PRESCRICAO_DEVOLVIDA = 'prescricao-devolvida', // Devolvido
}

export enum TipoProcedimentoEnum {
  RETIRADA_INFUSOR = 'retirada_infusor',
  PARACENTESE_ALIVIO = 'paracentese_alivio',
  MANUTENCAO_CTI = 'manutencao_cti',
  RETIRADA_PONTOS = 'retirada_pontos',
  TROCA_BOLSA = 'troca_bolsa',
  CURATIVO = 'curativo',
  MEDICACAO = 'medicacao'
}

export enum TipoConsultaEnum {
  TRIAGEM = 'triagem',
  NAVEGACAO = 'navegacao'
}

export type GrupoInfusao = 'rapido' | 'medio' | 'longo' | 'extra_longo' | 'indefinido';

export type TipoAgendamento = 'infusao' | 'procedimento' | 'consulta';

export interface DetalhesInfusao {
  prescricaoId: string;
  statusFarmacia: FarmaciaStatusEnum;
  tempoEstimadoPreparo?: number;
  horarioPrevisaoEntrega?: string;
  cicloAtual: number;
  diaCiclo: number;
  itensPreparados?: string[];
}

export interface DetalhesAgendamento {
  infusao?: DetalhesInfusao;
  procedimento?: {
    tipoProcedimento: TipoProcedimentoEnum;
    observacoes?: string;
  };
  consulta?: {
    tipoConsulta: TipoConsultaEnum;
    observacoes?: string;
  };
  remarcacao?: any;
}

export interface Agendamento {
  id: string;
  pacienteId: string;
  paciente?: {
    nome: string;
    registro: string;
    observacoesClinicas?: string
  };
  tipo: TipoAgendamento;
  data: string;
  criadoPorId?: string;
  criadoPor?: Profissional;
  turno: Turno;
  horarioInicio: string;
  horarioFim: string;
  checkin: boolean;
  status: AgendamentoStatusEnum;
  encaixe: boolean;
  observacoes?: string;
  tags?: string[];
  detalhes?: DetalhesAgendamento;
  prescricao?: PrescricaoMedica;
}
