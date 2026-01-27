import {UnidadeDoseEnum} from "@/types/protocoloTypes.ts";

interface DadosAntropometricos {
  peso?: number | null;
  altura?: number | null;
  sexo?: string;
  creatinina?: number | null;
  idade?: number;
}

interface ParamsCalculoDose {
  doseReferencia: number;
  unidade: UnidadeDoseEnum;
  pisoCreatinina?: number;
  tetoGfr?: number;
  percentualAjuste?: number;
  doseMaxima?: number;
}

export function usePrescricaoCalculos() {

  const calcularSC = (peso: number | null | undefined, altura: number | null | undefined): number => {
    if (!peso || !altura || peso <= 0 || altura <= 0) return 0;
    const res = 0.007184 * Math.pow(altura, 0.725) * Math.pow(peso, 0.425);
    return parseFloat(res.toFixed(2));
  };

  const calcularGFR = (dados: DadosAntropometricos, pisoCreatinina = 0.7, tetoGfr = 125): number => {
    const {peso, idade, sexo, creatinina} = dados;
    if (!peso || !idade || !sexo || !creatinina) return 0;
    const creatininaFinal = creatinina < pisoCreatinina ? pisoCreatinina : creatinina;
    let gfr = ((140 - idade) * peso) / (72 * creatininaFinal);
    if (sexo && ['F', 'FEMININO'].includes(sexo.toUpperCase())) gfr = gfr * 0.85;
    if (gfr > tetoGfr) return tetoGfr;
    return gfr;
  };

  const calcularDoseTeorica = (
    params: ParamsCalculoDose,
    dadosPaciente: DadosAntropometricos & { sc: number }
  ): number => {
    const {doseReferencia, unidade, pisoCreatinina, tetoGfr} = params;

    switch (unidade) {
      case UnidadeDoseEnum.MG_M2:
        return doseReferencia * (dadosPaciente.sc || 0);

      case UnidadeDoseEnum.MG_KG:
      case UnidadeDoseEnum.MCG_KG:
        return doseReferencia * (dadosPaciente.peso || 0);

      case UnidadeDoseEnum.AUC:
        const gfr = calcularGFR(dadosPaciente, pisoCreatinina, tetoGfr);
        return doseReferencia * (gfr + 25);

      case UnidadeDoseEnum.MG:
      case UnidadeDoseEnum.UI:
      case UnidadeDoseEnum.G:
      default:
        return doseReferencia;
    }
  };

  const calcularDoseFinal = (
    doseTeorica: number,
    percentualAjuste: number = 100,
    doseMaxima?: number | null
  ): number => {
    let calc = doseTeorica * (percentualAjuste / 100);
    if (doseMaxima && calc > doseMaxima) calc = doseMaxima;
    const precisao = calc < 1 ? 3 : 2;
    return parseFloat(calc.toFixed(precisao));
  };

  return {
    calcularSC,
    calcularGFR,
    calcularDoseTeorica,
    calcularDoseFinal
  };
}
