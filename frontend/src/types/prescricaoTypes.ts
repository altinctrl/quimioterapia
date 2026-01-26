import {CategoriaBlocoEnum, UnidadeDoseEnum, ViaAdministracaoEnum} from "@/types/protocoloTypes.ts";

export enum PrescricaoStatusEnum {
  PENDENTE = 'pendente',
  EM_CURSO = 'em-curso',
  CONCLUIDA = 'concluida',
  SUSPENSA = 'suspensa',
  CANCELADA = 'cancelada'
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
  idItem: string;
  medicamento: string;
  doseReferencia: string;
  unidade: UnidadeDoseEnum;
  doseMaxima?: number;
  doseTeorica?: number;
  percentualAjuste: number;
  doseFinal: number;
  via: ViaAdministracaoEnum;
  tempoMinutos: number;
  diluicaoFinal?: string;
  diasDoCiclo: number[];
  notasEspecificas?: string;
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
  observacoes?: string;
}

export interface PrescricaoMedica {
  id: string;
  pacienteId: string;
  medicoId: string;
  dataEmissao: string;
  status: PrescricaoStatusEnum;
  conteudo: ConteudoPrescricao;
}
