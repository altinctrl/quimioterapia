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

export interface PacienteImport {
  id?: string;
  nome: string;
  cpf: string;
  registro: string;
  dataNascimento: string
}
