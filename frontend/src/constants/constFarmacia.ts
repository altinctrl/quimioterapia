import {FarmaciaStatusEnum} from "@/types/typesAgendamento.ts";

export const STATUS_ORDER: Record<string, number> = {
  [FarmaciaStatusEnum.AGENDADO]: 0,
  [FarmaciaStatusEnum.AGUARDA_PRESCRICAO]: 1,
  [FarmaciaStatusEnum.VALIDANDO_PRESCRICAO]: 2,
  [FarmaciaStatusEnum.PENDENTE]: 3,
  [FarmaciaStatusEnum.EM_PREPARACAO]: 4,
  [FarmaciaStatusEnum.PRONTO]: 5,
  [FarmaciaStatusEnum.ENVIADO]: 6,
  [FarmaciaStatusEnum.MED_EM_FALTA]: 7,
  [FarmaciaStatusEnum.MED_JUD_EM_FALTA]: 8,
  [FarmaciaStatusEnum.SEM_PROCESSO]: 9,
  [FarmaciaStatusEnum.PRESCRICAO_DEVOLVIDA]: 10,
}
