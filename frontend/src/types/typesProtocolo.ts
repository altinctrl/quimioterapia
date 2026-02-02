export enum TipoTerapiaEnum {
  QUIMIOTERAPIA = "quimioterapia",
  IMUNOTERAPIA = "imunoterapia",
  TERAPIA_ALVO = "terapia_alvo",
  HORMONIOTERAPIA = "hormonioterapia",
  ANTICORPO_MONOCLONAL = "anticorpo_monoclonal",
  IMUNOGLOBULINA = "imunoglobulina",
  MEDICACAO_SUPORTE = "medicacao_suporte",
  HEMATOLOGIA = "hematologia",
}

export enum FaseEnum {
  ADJUVANTE = "Adjuvante",
  NEOADJUVANTE = "Neoadjuvante",
  PALIATIVO = "Paliativo",
  CONTROLE = "Controle",
  CURATIVO = "Curativo"
}

export enum CategoriaBlocoEnum {
  PRE_MED = "pre_med",
  QT = "qt",
  POS_MED_HOSPITALAR = "pos_med_hospitalar",
  POS_MED_DOMICILIAR = "pos_med_domiciliar",
}

export enum UnidadeDoseEnum {
  MG = "mg",
  MG_M2 = "mg/m2",
  MG_KG = "mg/kg",
  MCG_KG = "mcg/kg",
  AUC = "AUC",
  UI = "UI",
  G = "g"
}

export enum ViaAdministracaoEnum {
  IV = "IV",
  VO = "VO",
  SC = "SC",
  IT = "IT",
  IM = "IM"
}

export interface ConfiguracaoDiluicao {
  opcoesPermitidas?: string[];
  selecionada?: string;
}

export interface DetalhesMedicamento {
  tetoGfr: number | undefined;
  pisoCreatinina: number | undefined;
  medicamento: string;
  doseReferencia: number;
  unidade: UnidadeDoseEnum;
  doseMaxima?: number;
  via: ViaAdministracaoEnum;
  tempoMinutos: number;
  configuracaoDiluicao?: ConfiguracaoDiluicao;
  diasDoCiclo: number[];
  notasEspecificas?: string;
}

export interface MedicamentoUnico {
  tipo: 'medicamento_unico';
  dados: DetalhesMedicamento;
}

export interface GrupoAlternativas {
  tipo: 'grupo_alternativas';
  labelGrupo: string;
  opcoes: DetalhesMedicamento[];
}

export type ItemBloco = MedicamentoUnico | GrupoAlternativas;

export interface Bloco {
  ordem: number;
  categoria: CategoriaBlocoEnum;
  itens: ItemBloco[];
}

export interface TemplateCiclo {
  idTemplate: string;
  aplicavelAosCiclos?: string;
  blocos: Bloco[];
}

export interface Protocolo {
  id: string;
  nome: string;
  indicacao?: string;
  tempoTotalMinutos: number;
  duracaoCicloDias: number;
  totalCiclos?: number;
  fase?: FaseEnum;
  linha?: number;
  tipoTerapia?: string;
  observacoes?: string;
  precaucoes?: string;
  ativo: boolean;
  diasSemanaPermitidos?: number[];
  templatesCiclo: TemplateCiclo[];
  createdAt?: string;
}

export interface ProtocoloFiltros {
  sortOrder: 'nome' | 'duracao';
  status: 'todos' | 'ativos' | 'inativos';
  restricao: 'todos' | 'com' | 'sem';
  grupoInfusao: string[];
}
