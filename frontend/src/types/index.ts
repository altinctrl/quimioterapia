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

export interface Agendamento {
  id: string;
  pacienteId: string;
  paciente?: {
      nome: string;
      registro: string;
  };
  data: string;
  turno: Turno;
  horarioInicio: string;
  horarioFim: string;
  status: StatusPaciente;
  statusFarmacia: StatusFarmacia;
  encaixe: boolean;
  observacoes?: string;
  tags?: string[];
  tempoEstimadoPreparo?: number;
  horarioPrevisaoEntrega?: string;
  cicloAtual?: number;
  diaCiclo?: string;
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
}

export interface ConfigStatus {
  id: string;
  label: string;
  cor: string;
  tipo: 'paciente' | 'farmacia';
}