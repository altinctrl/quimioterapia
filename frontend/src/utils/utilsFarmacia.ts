import {Agendamento, MedicamentoFarmacia} from "@/types/typesAgendamento.ts";

export const getUnidadeFinal = (unidade: string) => {
  if (!unidade) return ''
  if (unidade.includes('/')) {
    return unidade.split('/')[0]
  }
  return unidade
}

export function extrairMedicamentosDoAgendamento(ag: Agendamento): MedicamentoFarmacia[] {
  const infoInfusao = ag.detalhes?.infusao;
  const prescricao = ag.prescricao;
  const diaCicloAtual = infoInfusao?.diaCiclo || 1;
  const itensPreparados = new Set(infoInfusao?.itensPreparados || []);

  const medicamentos: MedicamentoFarmacia[] = [];

  if (prescricao && prescricao.conteudo && prescricao.conteudo.blocos) {
    prescricao.conteudo.blocos.forEach(bloco => {
      bloco.itens.forEach(item => {
        if (item.diasDoCiclo.includes(diaCicloAtual)) {
          const key = item.idItem || `${bloco.ordem}-${item.medicamento}`;

          medicamentos.push({
            key: key,
            nome: item.medicamento,
            dose: String(item.doseFinal),
            unidade: getUnidadeFinal(item.unidade),
            checked: itensPreparados.has(key)
          });
        }
      });
    });
  }

  return medicamentos;
}
