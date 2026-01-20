import {CategoriaBlocoEnum} from "@/types";

export const diasSemanaOptions = [
  {value: 1, label: 'Segunda'},
  {value: 2, label: 'Terça'},
  {value: 3, label: 'Quarta'},
  {value: 4, label: 'Quinta'},
  {value: 5, label: 'Sexta'}
]

export const categoriasBloco = [
  {value: CategoriaBlocoEnum.PRE_MED, label: 'Pré-Medicação'},
  {value: CategoriaBlocoEnum.QT, label: 'Terapia'},
  {value: CategoriaBlocoEnum.POS_MED_HOSPITALAR, label: 'Pós-Med (Hospitalar)'},
  {value: CategoriaBlocoEnum.POS_MED_DOMICILIAR, label: 'Pós-Med (Domiciliar)'},
  {value: CategoriaBlocoEnum.INFUSOR, label: 'Infusor'}
]

export const diluentesDisponiveis = [
  "Soro Fisiológico 0,9% 50ml",
  "Soro Fisiológico 0,9% 100ml",
  "Soro Fisiológico 0,9% 250ml",
  "Soro Fisiológico 0,9% 500ml",
  "Soro Fisiológico 0,9% 1000ml",
  "Glicose 5% 50ml",
  "Glicose 5% 100ml",
  "Glicose 5% 250ml",
  "Glicose 5% 500ml",
  "Glicose 5% 1000ml",
  "Água para Injeção 10ml",
  "Sem Diluente (Bolus)"
]
