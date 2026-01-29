import {
  Bloco,
  CategoriaBlocoEnum,
  DetalhesMedicamento,
  ItemBloco,
  Protocolo,
  TemplateCiclo,
  UnidadeDoseEnum,
  ViaAdministracaoEnum
} from "@/types/typesProtocolo.ts";

export const createEmptyMedicamento = (): DetalhesMedicamento => ({
  medicamento: '',
  doseReferencia: 0,
  doseMaxima: undefined,
  unidade: UnidadeDoseEnum.MG_M2,
  via: ViaAdministracaoEnum.IV,
  tetoGfr: undefined,
  pisoCreatinina: undefined,
  tempoMinutos: 0,
  diasDoCiclo: [1],
  notasEspecificas: '',
  configuracaoDiluicao: {opcoesPermitidas: [], selecionada: ''}
})

export const createEmptyItemBloco = (): ItemBloco => ({
  tipo: 'medicamento_unico',
  dados: createEmptyMedicamento()
})

export const createEmptyBloco = (ordem: number): Bloco => ({
  ordem,
  categoria: CategoriaBlocoEnum.QT,
  itens: []
})

export const createEmptyTemplate = (nome: string = 'Padrão'): TemplateCiclo => ({
  idTemplate: nome,
  aplicavelAosCiclos: '',
  blocos: []
})

export const createEmptyProtocolo = (): Partial<Protocolo> => ({
  nome: '',
  indicacao: '',
  fase: undefined,
  linha: undefined,
  tempoTotalMinutos: 0,
  duracaoCicloDias: 21,
  totalCiclos: 0,
  observacoes: '',
  precaucoes: '',
  ativo: true,
  diasSemanaPermitidos: [],
  templatesCiclo: [createEmptyTemplate('Padrão')]
})
