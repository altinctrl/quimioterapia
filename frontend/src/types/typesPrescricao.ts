import {
  CategoriaBlocoEnum,
  DetalhesMedicamento,
  UnidadeDoseEnum,
  ViaAdministracaoEnum
} from "@/types/typesProtocolo.ts";

export enum PrescricaoStatusEnum {
  PENDENTE = 'pendente',
  AGENDADA = 'agendada',
  EM_CURSO = 'em-curso',
  CONCLUIDA = 'concluida',
  SUSPENSA = 'suspensa',
  SUBSTITUIDA = 'substituida',
  CANCELADA = 'cancelada'
}

export interface ItemMedicamentoForm extends ItemPrescricaoConteudo {
  tipo: 'medicamento_unico';
}

export interface ItemGrupoForm {
  tipo: 'grupo_alternativas';
  labelGrupo: string;
  itemSelecionado: ItemPrescricaoConteudo | null;
  opcoes: DetalhesMedicamento[];
}

export type ItemBlocoForm = ItemMedicamentoForm | ItemGrupoForm;

export interface BlocoForm {
  ordem: number;
  categoria: CategoriaBlocoEnum;
  itens: ItemBlocoForm[];
}

export interface MedicoSnapshot {
  nome: string;
  crmUf: string;
}

export interface PacienteSnapshot {
  nome: string;
  prontuario: string;
  nascimento: string;
  sexo: string;
  peso: number;
  altura: number;
  sc: number;
  creatinina?: number;
}

export interface ProtocoloRef {
  nome: string;
  cicloAtual: number;
}

export interface ItemPrescricaoConteudo {
  idItem?: string;
  medicamento: string;
  doseReferencia: number;
  unidade: UnidadeDoseEnum;
  doseMaxima?: number | null;
  doseTeorica?: number | null;
  percentualAjuste: number;
  doseFinal: number;
  via: ViaAdministracaoEnum;
  tempoMinutos: number;
  diluicaoFinal?: string;
  diasDoCiclo: number[];
  notasEspecificas?: string | null;
}

export interface BlocoPrescricao {
  ordem: number;
  categoria: CategoriaBlocoEnum;
  itens: ItemPrescricaoConteudo[];
}

export interface ConteudoPrescricao {
  dataEmissao: string;
  paciente: PacienteSnapshot;
  medico: MedicoSnapshot;
  protocolo: ProtocoloRef;
  blocos: BlocoPrescricao[];
  diagnostico?: string;
}

export interface PrescricaoStatusHistoricoItem {
  data: string;
  usuarioId?: string;
  usuarioNome?: string;
  statusAnterior: PrescricaoStatusEnum;
  statusNovo: PrescricaoStatusEnum;
  motivo?: string;
}

export interface PrescricaoHistoricoAgendamentoItem {
  data: string;
  agendamentoId: string;
  statusAgendamento: string;
  usuarioId?: string;
  usuarioNome?: string;
  observacoes?: string;
}

export interface PrescricaoMedica {
  id: string;
  pacienteId: string;
  medicoId: string;
  dataEmissao: string;
  status: PrescricaoStatusEnum;
  conteudo: ConteudoPrescricao;
  historicoStatus?: PrescricaoStatusHistoricoItem[];
  historicoAgendamentos?: PrescricaoHistoricoAgendamentoItem[];
  prescricaoSubstitutaId?: string | null;
  prescricaoOriginalId?: string | null;
}
