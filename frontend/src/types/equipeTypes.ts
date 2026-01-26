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
