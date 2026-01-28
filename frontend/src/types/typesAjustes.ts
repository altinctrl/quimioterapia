export interface ParametrosAgendamento {
  horarioAbertura: string;
  horarioFechamento: string;
  diasFuncionamento: number[];
  vagas: {
    infusao_rapido: number;
    infusao_medio: number;
    infusao_longo: number;
    infusao_extra_longo: number;
    consultas: number;
    procedimentos: number;
  };
  tags: string[];
  cargos: string[];
  funcoes: string[];
  diluentes: string[];
}

export interface ConfigStatus {
  id: string;
  label: string;
  cor: string;
  corBadge?: string;
  tipo: 'paciente' | 'farmacia';
}
