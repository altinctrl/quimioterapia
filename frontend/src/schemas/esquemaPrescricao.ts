import {z} from 'zod';
import {toTypedSchema} from '@vee-validate/zod';
import {
  BlocoForm,
  ItemMedicamentoForm
} from "@/types/typesPrescricao.ts";
import {
  sequenciaEstaCorreta,
  temOrdensDuplicadas,
  transformToNumber,
  verificarPresencaUnidade
} from "@/utils/utilsPrescricao.ts";
import {
  CategoriaBlocoEnum,
  DetalhesMedicamento,
  UnidadeDoseEnum,
  ViaAdministracaoEnum
} from "@/types/typesProtocolo.ts";

const validarRegrasMedicamento = (data: ItemMedicamentoForm, ctx: z.RefinementCtx) => {
  if (data.via === ViaAdministracaoEnum.VO) {
    if (data.diluicaoFinal) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Medicamentos VO não devem ter diluição',
        path: ['diluicaoFinal']
      });
    }
    if (data.tempoMinutos > 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Medicamentos VO não possuem tempo de infusão',
        path: ['tempoMinutos']
      });
    }
  }
  if ([ViaAdministracaoEnum.IV].includes(data.via) && !data.diluicaoFinal) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'A diluição é obrigatória para esta via de administração',
      path: ['diluicaoFinal']
    });
  }
  if (data.via === 'IV' && (data.tempoMinutos || 0) <= 0) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'Defina um tempo de infusão para administração IV',
      path: ['tempoMinutos']
    });
  }
  if (data.doseMaxima && data.doseFinal > data.doseMaxima) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'A dose final não pode exceder a dose máxima permitida',
      path: ['doseFinal']
    });
  }
};

const numberSchema = z.preprocess(
  transformToNumber,
  z.number({invalid_type_error: 'Valor inválido'})
    .nonnegative('O valor não pode ser negativo')
    .nullable()
    .optional()
);

const requiredNumberSchema = z.preprocess(
  transformToNumber,
  z.number({required_error: 'Campo obrigatório', invalid_type_error: 'Valor inválido'})
    .positive('Deve ser maior que zero')
);

export const itemPrescricaoSchema = z.object({
  idItem: z.string().optional(),
  tipo: z.literal('medicamento_unico').default('medicamento_unico'),
  medicamento: z.string().min(1, 'Medicamento obrigatório'),
  doseReferencia: requiredNumberSchema,
  unidade: z.nativeEnum(UnidadeDoseEnum),
  doseMaxima: numberSchema.refine(val => val === null || val === undefined || val > 0, {
    message: "A dose máxima deve ser maior que zero"
  }).optional(),
  doseTeorica: numberSchema,
  percentualAjuste: z.preprocess(
    transformToNumber,
    z.number({invalid_type_error: 'Valor inválido'}).min(0).max(500).default(100)
  ),
  doseFinal: numberSchema,
  pisoCreatinina: z.preprocess(
    transformToNumber,
    z.number({invalid_type_error: 'Valor inválido'}).min(0).nullable().optional()
  ),
  tetoGfr: z.preprocess(
    transformToNumber,
    z.number({invalid_type_error: 'Valor inválido'}).min(0).nullable().optional()
  ),
  via: z.nativeEnum(ViaAdministracaoEnum),
  tempoMinutos: z.preprocess(
    transformToNumber,
    z.number({invalid_type_error: 'Valor inválido'}).int().min(0).default(0)
  ),
  diluicaoFinal: z.string().optional(),
  diasDoCiclo: z.union([z.string(), z.array(z.number())])
    .superRefine((val, ctx) => {
      if (typeof val === 'string') {
        if (!val.trim()) return;

        if (/[^0-9,\s]/.test(val)) {
           ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: 'Digite apenas números (ex: 1, 8, 15)'
          });
          return z.NEVER;
        }

        const parts = val.split(',');
        for (const part of parts) {
          const trimmed = part.trim();
          if (trimmed.includes(' ')) {
            ctx.addIssue({
              code: z.ZodIssueCode.custom,
              message: 'Separe os números por vírgula (ex: 1, 8)'
            });
            return z.NEVER;
          }
        }
      }
    })
    .transform((val, ctx) => {
      if (Array.isArray(val)) return val;

      const parts = val.split(',').map(s => s.trim()).filter(s => s !== '');
      const numbers = parts.map(Number);

      if (numbers.some(n => isNaN(n))) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Números inválidos' });
        return z.NEVER;
      }
      return numbers;
    })
    .pipe(
      z.array(z.number().int().positive('Os dias devem ser positivos'))
       .min(1, 'Informe os dias de administração')
       .refine((items) => new Set(items).size === items.length, {
         message: 'Não deve haver dias repetidos'
       })
    ),
  notasEspecificas: z.string().nullish(),
});

export const itemGrupoSchema = z.object({
  tipo: z.literal('grupo_alternativas'),
  labelGrupo: z.string(),
  itemSelecionado: itemPrescricaoSchema.nullable().superRefine((val, ctx) => {
    if (!val) {
      ctx.addIssue({code: z.ZodIssueCode.custom, message: 'Selecione uma opção'});
      return;
    }
    validarRegrasMedicamento(val as ItemMedicamentoForm, ctx);
  }),
  opcoes: z.array(z.custom<DetalhesMedicamento>())
});

export const blocoSchema = z.object({
  ordem: z.number(),
  categoria: z.nativeEnum(CategoriaBlocoEnum),
  itens: z.array(z.discriminatedUnion('tipo', [
      itemPrescricaoSchema,
      itemGrupoSchema
    ]).superRefine((item, ctx) => {
      if (item.tipo === 'medicamento_unico') validarRegrasMedicamento(item as unknown as ItemMedicamentoForm, ctx);
    })
  )
});

export const prescricaoFormSchema = z.object({
  pacienteId: z.string().min(1, 'Selecione um paciente'),
  peso: requiredNumberSchema.refine(v => v < 600, 'Peso excede o limite de segurança'),
  altura: requiredNumberSchema,
  creatinina: numberSchema,
  sc: numberSchema,
  idade: z.number(),
  sexo: z.string(),
  duracaoCicloDias: z.number().optional(),
  diagnostico: z.string().min(1, 'Informe o diagnóstico'),
  protocoloNome: z.string().min(1, 'Protocolo é obrigatório'),
  numeroCiclo: z.preprocess(transformToNumber, z.number().int().min(0).default(1)),
  blocos: z.array(blocoSchema).default([])
}).superRefine((data, ctx) => {
  const blocos = data.blocos as BlocoForm[];
  if (verificarPresencaUnidade(blocos, UnidadeDoseEnum.AUC)) {
    if (!data.creatinina || data.creatinina <= 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Creatinina é obrigatória para medicamentos com dose AUC',
        path: ['creatinina']
      });
      if (!data.idade || data.idade <= 0) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: 'Idade do paciente é necessária para cálculo de AUC',
          path: ['pacienteId']
        });
      }
      if (!data.sexo) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: 'Sexo do paciente é necessário para o cálculo de AUC (ajuste GFR)',
          path: ['pacienteId']
        });
      }
    }
  }
  if (verificarPresencaUnidade(blocos, UnidadeDoseEnum.MG_M2) && (!data.sc || data.sc <= 0)) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'SC obrigatória para doses em mg/m²',
      path: ['sc']
    });
  }
  if (data.duracaoCicloDias) {
    blocos.forEach((bloco, bIdx) => {
      bloco.itens.forEach((item, iIdx) => {
        const dias = item.tipo === 'medicamento_unico'
          ? item.diasDoCiclo
          : item.itemSelecionado?.diasDoCiclo || [];

        if (Array.isArray(dias)) {
          const diaInvalido = dias.find(d => d > (data.duracaoCicloDias || 0));
          if (diaInvalido) {
            ctx.addIssue({
              code: z.ZodIssueCode.custom,
              message: `Dia ${diaInvalido} excede a duração do ciclo (${data.duracaoCicloDias} dias)`,
              path: ['blocos', bIdx, 'itens', iIdx, 'diasDoCiclo']
            });
          }
        }
      });
    });
  }
  if (temOrdensDuplicadas(blocos)) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'Existem blocos com números de ordem duplicados',
      path: ['blocos']
    });
  }
  if (!sequenciaEstaCorreta(blocos)) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'A sequência dos blocos deve ser contínua (ex: 1, 2, 3...)',
      path: ['blocos']
    });
  }
});

export const typedPrescricaoSchema = toTypedSchema(prescricaoFormSchema);
export type PrescricaoFormValues = z.infer<typeof prescricaoFormSchema>;
