import {PrescricaoMedica} from "@/types/typesPrescricao.ts";

import {Profissional} from "@/types/typesEquipe.ts";

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
  AGENDADO = 'agendado',
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

export interface HistoricoPrescricaoAgendamentoItem {
  data: string;
  usuarioId?: string;
  usuarioNome?: string;
  prescricaoIdAnterior?: string | null;
  prescricaoIdNova?: string | null;
  motivo?: string;
}

export interface AgendamentoHistoricoItem {
  data: string;
  usuarioId?: string;
  usuarioNome?: string;
  tipoAlteracao: string;
  valorAntigo?: string | null;
  valorNovo?: string | null;
  motivo?: string;
  campo?: string;
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
  historicoPrescricoes?: HistoricoPrescricaoAgendamentoItem[];
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
  historicoAlteracoes?: AgendamentoHistoricoItem[];
}

export interface FiltrosAgenda {
  ordenacao: string
  turno: string
  statusFarmacia: string[]
  gruposInfusao: string[]
  esconderRemarcados: boolean
}

export interface FiltrosFarmacia {
  ordenacao: string
  turno: string
  status: string[]
}

export interface MedicamentoFarmacia {
  key: string
  nome: string
  dose: string
  unidade: string
  checked: boolean
}

export interface FarmaciaTableRow {
  id: string
  pacienteId: string
  horario: string
  pacienteNome: string
  pacienteRegistro: string
  observacoesClinicas: string | undefined
  protocoloNome: string
  checkin: boolean
  statusTexto: string
  statusBloqueado: boolean
  statusFarmacia: FarmaciaStatusEnum
  statusFarmaciaCor: string
  previsaoEntrega: string
  medicamentos: Array<{
    key: string
    nome: string
    dose: string
    unidade: string
    checked: boolean
  }>
  checklistLabel: string
  hasMedicamentos: boolean
}
