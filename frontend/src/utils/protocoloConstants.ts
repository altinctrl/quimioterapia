import {CategoriaBlocoEnum} from "@/types/protocoloTypes.ts";

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
