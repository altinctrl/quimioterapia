import uuid
from datetime import datetime
from typing import Optional

from src.models.auth_model import User
from src.models.paciente_model import Paciente
from src.models.protocolo_model import Protocolo
from src.schemas.prescricao_schema import (
    PacienteSnapshot, MedicoSnapshot, ProtocoloRef, BlocoPrescricao, ItemPrescricao, UnidadeDoseEnum
)
from src.schemas.protocolo_schema import TemplateCiclo
from src.scripts.seed_utils.helpers import calcular_bsa


def criar_prescricao_payload(
        protocolo_model: Protocolo,
        paciente: Paciente,
        medico_obj: User,
        ciclo: int,
) -> dict:
    bsa = calcular_bsa(paciente.peso, paciente.altura)
    templates_data = protocolo_model.templates_ciclo
    templates = [TemplateCiclo(**t) if isinstance(t, dict) else t for t in templates_data]
    template = templates[0]

    blocos_prescricao = []

    for bloco in template.blocos:
        itens_presc = []
        for item_bloco in bloco.itens:
            dados = getattr(item_bloco, 'dados', None)
            tipo = getattr(item_bloco, 'tipo', None)

            if isinstance(item_bloco, dict):
                tipo = item_bloco.get('tipo')
                dados = item_bloco.get('dados')

            if tipo == 'medicamento_unico' and dados:
                dose_calc = dados.dose_referencia
                if dados.unidade == UnidadeDoseEnum.MG_M2:
                    dose_calc = dados.dose_referencia * bsa
                elif dados.unidade == UnidadeDoseEnum.MG_KG:
                    dose_calc = dados.dose_referencia * paciente.peso

                diluicao_padrao = ""
                if hasattr(dados, 'configuracao_diluicao') and dados.configuracao_diluicao:
                    config = dados.configuracao_diluicao
                    diluicao_padrao = getattr(config, 'selecionada', "") or ""
                    if not diluicao_padrao and hasattr(config, 'opcoes_permitidas') and config.opcoes_permitidas:
                        diluicao_padrao = config.opcoes_permitidas[0]

                item_p = ItemPrescricao(
                    id_item=str(uuid.uuid4()),
                    medicamento=dados.medicamento,
                    dose_referencia=str(dados.dose_referencia),
                    unidade=dados.unidade,
                    dose_teorica=round(dose_calc, 2),
                    percentual_ajuste=100.0,
                    dose_final=round(dose_calc, 2),
                    via=dados.via,
                    tempo_minutos=dados.tempo_minutos,
                    diluicao_final=diluicao_padrao,
                    dias_do_ciclo=dados.dias_do_ciclo,
                    notas_especificas=dados.notas_especificas
                )
                itens_presc.append(item_p)

        if itens_presc:
            bloco_p = BlocoPrescricao(
                ordem=bloco.ordem,
                categoria=bloco.categoria,
                itens=itens_presc
            )
            blocos_prescricao.append(bloco_p)

    paciente_snapshot = PacienteSnapshot(
        nome=paciente.nome,
        prontuario=paciente.registro,
        nascimento=paciente.data_nascimento,
        sexo=paciente.sexo,
        peso=paciente.peso,
        altura=paciente.altura,
        sc=round(bsa, 2)
    )

    medico_snapshot = MedicoSnapshot(
        nome=medico_obj.display_name,
        crm_uf=medico_obj.registro_profissional if medico_obj.registro_profissional else "CRM-UF 00000"
    )

    protocolo_ref = ProtocoloRef(
        nome=protocolo_model.nome,
        ciclo_atual=ciclo
    )

    documento_json = {
        "data_emissao": datetime.now().isoformat(),
        "paciente": paciente_snapshot.model_dump(mode='json'),
        "medico": medico_snapshot.model_dump(mode='json'),
        "protocolo": protocolo_ref.model_dump(mode='json'),
        "blocos": [b.model_dump(mode='json') for b in blocos_prescricao],
        "diagnostico": "Gerado via seed com validação Pydantic."
    }

    return documento_json


def criar_historico_status_inicial(status_atual: str) -> list[dict]:
    return [{
        "data": datetime.now().isoformat(),
        "usuario_id": "seed",
        "usuario_nome": "Seed",
        "status_anterior": status_atual,
        "status_novo": status_atual,
        "motivo": "Seed inicial"
    }]


def criar_historico_agendamento(
        ag_id: str,
        status_agendamento,
) -> dict:
    status_val = status_agendamento.value if hasattr(status_agendamento, 'value') else str(status_agendamento)
    return {
        "data": datetime.now().isoformat(),
        "agendamento_id": ag_id,
        "status_agendamento": status_val,
        "usuario_id": "seed",
        "usuario_nome": "Seed",
        "observacoes": "Agendamento criado via seed"
    }


def criar_historico_alteracao_agendamento(
        tipo: str,
        campo: str,
        valor_antigo: Optional[str],
        valor_novo: Optional[str],
) -> dict:
    return {
        "data": datetime.now().isoformat(),
        "usuario_id": "seed",
        "usuario_nome": "Seed",
        "tipo_alteracao": tipo,
        "campo": campo,
        "valor_antigo": valor_antigo,
        "valor_novo": valor_novo,
        "motivo": "Seed inicial"
    }
