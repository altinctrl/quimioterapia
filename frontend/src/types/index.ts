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

export type StatusPaciente =
  | 'agendado'
  | 'em-triagem'
  | 'aguardando-consulta'
  | 'aguardando-exame'
  | 'aguardando-medicamento'
  | 'em-infusao'
  | 'pos-qt'
  | 'intercorrencia'
  | 'internado'
  | 'suspenso'
  | 'ausente'
  | 'remarcado'
  | 'obito'
  | 'concluido';

export type StatusFarmacia = | 'pendente' | 'em-preparacao' | 'pronta' | 'enviada';

export type GrupoInfusao = 'rapido' | 'medio' | 'longo';

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
  idade?: number;
  telefone?: string;
  email?: string;
  peso?: number;
  altura?: number;
  contatosEmergencia?: ContatoEmergencia[];
  observacoesClinicas?: string;
  protocoloId?: string;
}

export interface ItemProtocolo {
  id?: number;
  nome: string;
  dosePadrao?: string;
  unidadePadrao?: string;
  viaPadrao?: string;
  tipo?: 'pre' | 'qt' | 'pos';
}

export interface Protocolo {
  id: string;
  nome: string;
  descricao?: string;
  indicacao?: string;
  duracao: number;
  frequencia: string;
  numeroCiclos: number;
  grupoInfusao: GrupoInfusao;
  medicamentos: ItemProtocolo[];
  preMedicacoes: ItemProtocolo[];
  posMedicacoes: ItemProtocolo[];
  observacoes?: string;
  precaucoes?: string;
  ativo: boolean;
  diasSemanaPermitidos?: number[];
  createdAt?: string;
}

export interface ItemPrescricao {
  id?: number;
  nome: string;
  dose?: string;
  unidade?: string;
  via?: string;
  tempoInfusao?: number;
  veiculo?: string;
  volumeVeiculo?: string;
  observacoes?: string;
  ordem?: number;
  tipo: 'pre' | 'qt' | 'pos';
}

export interface PrescricaoMedica {
  id: string;
  pacienteId: string;
  medicoNome: string;
  protocolo?: string;
  protocoloId?: string;
  dataPrescricao: string;
  cicloAtual: number;
  ciclosTotal: number;
  medicamentos: ItemPrescricao[];
  qt: ItemPrescricao[];
  posMedicacoes: ItemPrescricao[];
  observacoes?: string;
  status: 'ativa' | 'pausada' | 'concluida' | 'cancelada';
  peso?: number;
  altura?: number;
  superficieCorporea?: number;
  diagnostico?: string;
}

export type TipoAgendamento = 'infusao' | 'procedimento' | 'consulta';

export interface DetalhesInfusao {
  status_farmacia: StatusFarmacia;
  tempo_estimado_preparo?: number;
  horario_previsao_entrega?: string;
  ciclo_atual?: number;
  dia_ciclo?: string;
}

export interface DetalhesAgendamento {
  infusao?: DetalhesInfusao;
  procedimento?: any;
  consulta?: any;
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
  status: StatusPaciente;
  encaixe: boolean;
  observacoes?: string;
  tags?: string[];
  detalhes?: DetalhesAgendamento;
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
  username: string
  nome: string
  cargo: string
  coren?: string
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
