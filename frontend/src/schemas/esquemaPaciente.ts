import {z} from 'zod'
import {toTypedSchema} from '@vee-validate/zod'

export const buscaPacienteSchema = z.object({
  termo: z.string().min(3, 'Digite pelo menos 3 caracteres para buscar')
})

export const contatoEmergenciaSchema = z.object({
  nome: z.string().min(1, 'Nome é obrigatório'),
  parentesco: z.string().min(1, 'Parentesco é obrigatório'),
  telefone: z.string().min(8, 'Telefone inválido')
})

export const esquemaPaciente = z.object({
  nome: z.string().min(3, 'Nome deve ter no mínimo 3 caracteres'),
  cpf: z.string().min(11, 'CPF incompleto').max(14, 'CPF inválido'),
  registro: z.string().optional(),
  dataNascimento: z.string().refine((data) => {
    if (!data) return true
    return new Date(data) <= new Date()
  }, 'Data de nascimento não pode ser no futuro'),
  sexo: z.enum(['M', 'F'], {errorMap: () => ({message: 'Selecione o sexo'})}),
  peso: z.preprocess(
    (val) => (val === '' || val === null || val === undefined ? null : Number(val)),
    z.number().min(0).max(1000).nullable().optional()
  ),
  altura: z.preprocess(
    (val) => (val === '' || val === null || val === undefined ? null : Number(val)),
    z.number().min(0).max(500).nullable().optional()
  ),
  telefone: z.preprocess((val) => (val === '' ? null : val), z.string().nullable().optional()),
  email: z.preprocess(
    (val) => (val === '' ? null : val),
    z.string().email('E-mail inválido').nullable().optional()
  ),
  observacoesClinicas: z.string().nullable().optional(),
  contatosEmergencia: z.array(contatoEmergenciaSchema).optional().default([])
})

export const buscaPacienteFormSchema = toTypedSchema(buscaPacienteSchema)
export const pacienteFormSchema = toTypedSchema(esquemaPaciente)
export type PacienteFormValues = z.infer<typeof esquemaPaciente>
