import {z} from 'zod';

const customErrorMap: z.ZodErrorMap = (issue, ctx) => {
  let message = ctx.defaultError;

  switch (issue.code) {
    case z.ZodIssueCode.invalid_type:
      if (issue.received === 'undefined' || issue.received === 'null') {
        message = 'Campo obrigatório';
      } else {
        message = 'Tipo de dado inválido';
      }
      break;
    case z.ZodIssueCode.invalid_date:
      message = 'Data inválida';
      break;
    case z.ZodIssueCode.invalid_string:
      if (issue.validation === 'email') {
        message = 'E-mail inválido';
      } else if (issue.validation === 'url') {
        message = 'URL inválida';
      } else if (issue.validation === 'uuid') {
        message = 'ID inválido';
      }
      break;
    case z.ZodIssueCode.too_small:
      if (issue.type === 'string') {
        if (issue.minimum === 1) {
          message = 'Campo obrigatório';
        } else {
          message = `Deve ter pelo menos ${issue.minimum} caractere(s)`;
        }
      } else if (issue.type === 'number') {
        message = `Deve ser maior ou igual a ${issue.minimum}`;
      } else if (issue.type === 'array') {
        message = `Selecione pelo menos ${issue.minimum} item(s)`;
      }
      break;
    case z.ZodIssueCode.too_big:
      if (issue.type === 'string') {
        message = `Deve ter no máximo ${issue.maximum} caractere(s)`;
      } else if (issue.type === 'number') {
        message = `Deve ser menor ou igual a ${issue.maximum}`;
      } else if (issue.type === 'array') {
        message = `Selecione no máximo ${issue.maximum} item(s)`;
      }
      break;
  }

  return {message};
};

export function setupZod() {
  z.setErrorMap(customErrorMap);
}
