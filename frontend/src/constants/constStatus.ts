import {AgendamentoStatusEnum, FarmaciaStatusEnum} from "@/types/typesAgendamento.ts";

export const LABELS_STATUS_AGENDAMENTO: Record<AgendamentoStatusEnum, string> = {
  [AgendamentoStatusEnum.AGENDADO]: 'Agendado',
  [AgendamentoStatusEnum.AGUARDANDO_CONSULTA]: 'Aguardando Consulta',
  [AgendamentoStatusEnum.AGUARDANDO_EXAME]: 'Aguardando Exame',
  [AgendamentoStatusEnum.AGUARDANDO_MEDICAMENTO]: 'Aguardando Medicação',
  [AgendamentoStatusEnum.INTERNADO]: 'Internado',
  [AgendamentoStatusEnum.SUSPENSO]: 'Suspenso',
  [AgendamentoStatusEnum.REMARCADO]: 'Remarcado',
  [AgendamentoStatusEnum.EM_TRIAGEM]: 'Em Triagem',
  [AgendamentoStatusEnum.EM_INFUSAO]: 'Em Infusão',
  [AgendamentoStatusEnum.INTERCORRENCIA]: 'Intercorrência',
  [AgendamentoStatusEnum.CONCLUIDO]: 'Concluído'
};

export const LABELS_STATUS_FARMACIA: Record<FarmaciaStatusEnum, string> = {
  [FarmaciaStatusEnum.AGENDADO]: 'Agendado',
  [FarmaciaStatusEnum.AGUARDA_PRESCRICAO]: 'Aguarda Prescrição',
  [FarmaciaStatusEnum.VALIDANDO_PRESCRICAO]: 'Validando Prescrição',
  [FarmaciaStatusEnum.PENDENTE]: 'Pendente',
  [FarmaciaStatusEnum.EM_PREPARACAO]: 'Em Preparação',
  [FarmaciaStatusEnum.PRONTO]: 'Pronto',
  [FarmaciaStatusEnum.ENVIADO]: 'Enviado',
  [FarmaciaStatusEnum.MED_EM_FALTA]: 'Med. em Falta',
  [FarmaciaStatusEnum.MED_JUD_EM_FALTA]: 'Med. Jud. em Falta',
  [FarmaciaStatusEnum.SEM_PROCESSO]: 'Sem Processo',
  [FarmaciaStatusEnum.PRESCRICAO_DEVOLVIDA]: 'Prescrição Devolvida'
};

export const CORES_PADRAO_AGENDAMENTO: Record<AgendamentoStatusEnum, string> = {
  [AgendamentoStatusEnum.AGENDADO]: 'bg-slate-500 text-white hover:bg-slate-600',
  [AgendamentoStatusEnum.AGUARDANDO_CONSULTA]: 'bg-indigo-500 text-white hover:bg-indigo-600',
  [AgendamentoStatusEnum.AGUARDANDO_EXAME]: 'bg-violet-500 text-white hover:bg-violet-600',
  [AgendamentoStatusEnum.AGUARDANDO_MEDICAMENTO]: 'bg-purple-500 text-white hover:bg-purple-600',
  [AgendamentoStatusEnum.INTERNADO]: 'bg-orange-500 text-white hover:bg-orange-600',
  [AgendamentoStatusEnum.SUSPENSO]: 'bg-red-600 text-white hover:bg-red-700',
  [AgendamentoStatusEnum.REMARCADO]: 'bg-gray-200 text-gray-500 border-gray-300',
  [AgendamentoStatusEnum.EM_TRIAGEM]: 'bg-blue-500 text-white hover:bg-blue-600',
  [AgendamentoStatusEnum.EM_INFUSAO]: 'bg-green-600 text-white hover:bg-green-700',
  [AgendamentoStatusEnum.INTERCORRENCIA]: 'bg-amber-500 text-white hover:bg-amber-600',
  [AgendamentoStatusEnum.CONCLUIDO]: 'bg-teal-600 text-white hover:bg-teal-700'
};

export const CORES_PADRAO_FARMACIA: Record<FarmaciaStatusEnum, { cor: string, corBadge: string }> = {
  [FarmaciaStatusEnum.AGENDADO]: {
    cor: 'bg-red-600 text-white',
    corBadge: 'bg-gray-100 hover:bg-gray-100 text-gray-800 border-gray-200'
  },
  [FarmaciaStatusEnum.AGUARDA_PRESCRICAO]: {
    cor: 'bg-red-600 text-white',
    corBadge: 'bg-red-100 hover:bg-red-100 text-red-800 border-red-200'
  },
  [FarmaciaStatusEnum.VALIDANDO_PRESCRICAO]: {
    cor: 'bg-purple-500 text-white',
    corBadge: 'bg-yellow-100 hover:bg-yellow-100 text-yellow-800 border-yellow-200'
  },
  [FarmaciaStatusEnum.PENDENTE]: {
    cor: 'bg-yellow-500 text-white',
    corBadge: 'bg-gray-100 hover:bg-gray-100 text-gray-800 border-gray-200'
  },
  [FarmaciaStatusEnum.EM_PREPARACAO]: {
    cor: 'bg-blue-500 text-white',
    corBadge: 'bg-blue-100 hover:bg-blue-100 text-blue-800 border-blue-200'
  },
  [FarmaciaStatusEnum.PRONTO]: {
    cor: 'bg-green-500 text-white',
    corBadge: 'bg-green-100 hover:bg-green-100 text-green-800 border-green-200'
  },
  [FarmaciaStatusEnum.ENVIADO]: {
    cor: 'bg-gray-200 text-white',
    corBadge: 'bg-gray-100 hover:bg-gray-100 text-gray-800 border-gray-200'
  },
  [FarmaciaStatusEnum.MED_EM_FALTA]: {
    cor: 'bg-gray-200 text-white',
    corBadge: 'bg-red-100 hover:bg-red-100 text-red-800 border-red-200'
  },
  [FarmaciaStatusEnum.MED_JUD_EM_FALTA]: {
    cor: 'bg-gray-200 text-white',
    corBadge: 'bg-red-100 hover:bg-red-100 text-red-800 border-red-200'
  },
  [FarmaciaStatusEnum.SEM_PROCESSO]: {
    cor: 'bg-gray-200 text-white',
    corBadge: 'bg-red-100 hover:bg-red-100 text-red-800 border-red-200'
  },
  [FarmaciaStatusEnum.PRESCRICAO_DEVOLVIDA]: {
    cor: 'bg-gray-200 text-white',
    corBadge: 'bg-red-100 hover:bg-red-100 text-red-800 border-red-200'
  }
};
