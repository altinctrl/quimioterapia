export type UserRole = 'enfermeiro' | 'medico' | 'farmacia' | 'admin';

export interface User {
  id: string;
  nome: string;
  username: string;
  role: UserRole;
  grupo: string;
  email?: string;
  token?: string;
}

export type TipoUsuario = UserRole;
export type Usuario = User;

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
  PENDENTE = 'pendente',
  EM_PREPARACAO = 'em-preparacao',
  PRONTA = 'pronta',
  ENVIADA = 'enviada'
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
  INFUSOR = "infusor"
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

export enum PrescricaoStatusEnum {
  PENDENTE = 'pendente',
  EM_CURSO = 'em-curso',
  CONCLUIDA = 'concluida',
  SUSPENSA = 'suspensa',
  CANCELADA = 'cancelada'
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

export type GrupoInfusao = 'rapido' | 'medio' | 'longo';

export const opcoesProcedimento = [
  {value: TipoProcedimentoEnum.RETIRADA_INFUSOR, label: 'Retirada de Infusor'},
  {value: TipoProcedimentoEnum.PARACENTESE_ALIVIO, label: 'Paracentese de Alívio'},
  {value: TipoProcedimentoEnum.MANUTENCAO_CTI, label: 'Manutenção CTI'},
  {value: TipoProcedimentoEnum.RETIRADA_PONTOS, label: 'Retirada de Pontos'},
  {value: TipoProcedimentoEnum.TROCA_BOLSA, label: 'Troca de Bolsa'},
  {value: TipoProcedimentoEnum.CURATIVO, label: 'Curativo'},
  {value: TipoProcedimentoEnum.MEDICACAO, label: 'Medicação'}
]

export const opcoesConsulta = [
  {value: TipoConsultaEnum.TRIAGEM, label: 'Triagem'},
  {value: TipoConsultaEnum.NAVEGACAO, label: 'Navegação'}
]

export interface ContatoEmergencia {
  id?: number;
  nome: string;
  parentesco: string;
  telefone: string;
}

export interface Paciente {
  id: string;
  nome: string;
  cpf: string;
  registro: string;
  dataNascimento: string;
  sexo: string;
  idade?: number;
  telefone?: string;
  email?: string;
  peso?: number;
  altura?: number;
  contatosEmergencia?: ContatoEmergencia[];
  observacoesClinicas?: string;
  protocoloUltimaPrescricao?: string;
}

export interface ConfiguracaoDiluicao {
  opcoesPermitidas?: string[];
  selecionada?: string;
}

export interface DetalhesMedicamento {
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
  observacoes?: string;
  precaucoes?: string;
  ativo: boolean;
  diasSemanaPermitidos?: number[];
  templatesCiclo: TemplateCiclo[];
  createdAt?: string;
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

export function isInfusao(ag: Partial<Agendamento>): ag is Agendamento & { detalhes: { infusao: DetalhesInfusao } } {
  return !!ag.detalhes?.infusao;
}

export function isProcedimento(ag: Partial<Agendamento>): ag is Agendamento & { detalhes: { procedimento: any } } {
  return !!ag.detalhes?.procedimento;
}

export function isConsulta(ag: Partial<Agendamento>): ag is Agendamento & { detalhes: { consulta: any } } {
  return !!ag.detalhes?.consulta;
}

export interface ConfigGrupoInfusao {
  vagas: number;
  duracao: string;
}

export interface ParametrosAgendamento {
  horarioAbertura: string;
  horarioFechamento: string;
  diasFuncionamento: number[];
  gruposInfusao: {
    rapido: ConfigGrupoInfusao; medio: ConfigGrupoInfusao; longo: ConfigGrupoInfusao;
  };
  tags: string[];
  cargos: string[];
  funcoes: string[];
}

export interface ConfigStatus {
  id: string;
  label: string;
  cor: string;
  tipo: 'paciente' | 'farmacia';
}

export interface Profissional {
  username: string;
  nome: string;
  cargo: string
  registro?: string
  ativo: boolean
}

export interface EscalaPlantao {
  id: string
  data: string
  profissional_id: string
  funcao: string
  turno: 'Manhã' | 'Tarde' | 'Integral'
  profissional?: Profissional
}

export interface AusenciaProfissional {
  id: string
  profissional_id: string
  data_inicio: string
  data_fim: string
  motivo: string
  observacao?: string
  profissional?: Profissional
}

export const statusPermitidosSemCheckin = [
  AgendamentoStatusEnum.AGENDADO,
  AgendamentoStatusEnum.AGUARDANDO_CONSULTA,
  AgendamentoStatusEnum.AGUARDANDO_EXAME,
  AgendamentoStatusEnum.AGUARDANDO_MEDICAMENTO,
  AgendamentoStatusEnum.INTERNADO,
  AgendamentoStatusEnum.SUSPENSO,
  AgendamentoStatusEnum.REMARCADO
]
