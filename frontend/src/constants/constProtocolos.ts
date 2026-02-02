import {CategoriaBlocoEnum, TipoTerapiaEnum} from "@/types/typesProtocolo.ts";

export const diasSemanaOptions = [
  {value: 0, label: 'Domingo'},
  {value: 1, label: 'Segunda'},
  {value: 2, label: 'Terça'},
  {value: 3, label: 'Quarta'},
  {value: 4, label: 'Quinta'},
  {value: 5, label: 'Sexta'},
  {value: 6, label: 'Sábado'}
]

export const categoriasBloco = [
  {value: CategoriaBlocoEnum.PRE_MED, label: 'Pré-Medicação'},
  {value: CategoriaBlocoEnum.QT, label: 'Terapia'},
  {value: CategoriaBlocoEnum.POS_MED_HOSPITALAR, label: 'Pós-Med (Hospitalar)'},
  {value: CategoriaBlocoEnum.POS_MED_DOMICILIAR, label: 'Pós-Med (Domiciliar)'},
]

export const TipoTerapiaLabels: Record<TipoTerapiaEnum, string> = {
  [TipoTerapiaEnum.QUIMIOTERAPIA]: "Quimioterapia",
  [TipoTerapiaEnum.IMUNOTERAPIA]: "Imunoterapia",
  [TipoTerapiaEnum.TERAPIA_ALVO]: "Terapia Alvo",
  [TipoTerapiaEnum.HORMONIOTERAPIA]: "Hormonioterapia",
  [TipoTerapiaEnum.ANTICORPO_MONOCLONAL]: "Anticorpo Monoclonal",
  [TipoTerapiaEnum.IMUNOGLOBULINA]: "Imunoglobulina",
  [TipoTerapiaEnum.MEDICACAO_SUPORTE]: "Medicação de Suporte",
  [TipoTerapiaEnum.HEMATOLOGIA]: "Hematologia",
};
