import uuid
from datetime import date, datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm.attributes import flag_modified

from src.models.agendamento import Agendamento
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.controllers import prescricao_controller
from src.schemas.agendamento import AgendamentoCreate, AgendamentoUpdate, AgendamentoResponse, TipoAgendamento, \
    AgendamentoBulkUpdateList,  AgendamentoPrescricaoUpdate
from src.schemas.prescricao import PrescricaoResponse

def _aplicar_regras_atualizacao(
        agendamento: Agendamento,
        update_data: dict,
        usuario_id: str,
        usuario_nome: str,
) -> str:
    if 'tipo' in update_data:
        if update_data['tipo'] != agendamento.tipo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é permitido alterar o tipo de um agendamento. Cancele este e crie um novo."
            )
        del update_data['tipo']

    status_anterior = agendamento.status
    checkin_anterior = agendamento.checkin
    novo_status = update_data.get('status', agendamento.status)
    novo_checkin = update_data.get('checkin', agendamento.checkin)

    status_permitidos_sem_checkin = [
        'agendado',
        'aguardando-consulta',
        'aguardando-exame',
        'aguardando-medicamento',
        'internado',
        'suspenso',
        'remarcado'
    ]

    if not novo_checkin and novo_status not in status_permitidos_sem_checkin:
        if 'checkin' in update_data and update_data['checkin'] is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível remover o Check-in enquanto o paciente estiver com status '{novo_status}'."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O status '{novo_status}' exige que o paciente tenha realizado o Check-in."
            )

    prescricao_id_anterior = None
    if agendamento.tipo == TipoAgendamento.INFUSAO.value and agendamento.detalhes:
        prescricao_id_anterior = agendamento.detalhes.get('infusao', {}).get('prescricao_id')

    if 'detalhes' in update_data:
        novos_detalhes = update_data['detalhes']
        detalhes_atuais = dict(agendamento.detalhes) if agendamento.detalhes else {}

        mapa_tipo_chave = {
            TipoAgendamento.INFUSAO.value: 'infusao',
            TipoAgendamento.PROCEDIMENTO.value: 'procedimento',
            TipoAgendamento.CONSULTA.value: 'consulta'
        }
        tipo_chave_principal = mapa_tipo_chave.get(agendamento.tipo)
        chaves_proibidas = {v for k, v in mapa_tipo_chave.items() if v != tipo_chave_principal}

        for chave in novos_detalhes.keys():
            if chave in chaves_proibidas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Agendamento do tipo {agendamento.tipo} não pode ter detalhes de {chave}."
                )

        for chave, valor_novo in novos_detalhes.items():
            valor_atual = detalhes_atuais.get(chave)
            if isinstance(valor_atual, dict) and isinstance(valor_novo, dict):
                valor_atual.update(valor_novo)
            else:
                detalhes_atuais[chave] = valor_novo

        update_data['detalhes'] = detalhes_atuais

    for key, value in update_data.items():
        setattr(agendamento, key, value)

    if 'detalhes' in update_data:
        flag_modified(agendamento, "detalhes")

    historico_alteracoes = list(agendamento.historico_alteracoes or [])
    if 'status' in update_data and update_data['status'] != status_anterior:
        historico_alteracoes.append({
            "data": datetime.now().isoformat(),
            "usuario_id": usuario_id,
            "usuario_nome": usuario_nome,
            "tipo_alteracao": "status",
            "campo": "status",
            "valor_antigo": status_anterior,
            "valor_novo": update_data['status']
        })

    if 'checkin' in update_data and update_data['checkin'] != checkin_anterior:
        historico_alteracoes.append({
            "data": datetime.now().isoformat(),
            "usuario_id": usuario_id,
            "usuario_nome": usuario_nome,
            "tipo_alteracao": "checkin",
            "campo": "checkin",
            "valor_antigo": str(checkin_anterior),
            "valor_novo": str(update_data['checkin'])
        })

    if 'detalhes' in update_data and prescricao_id_anterior:
        prescricao_id_nova = agendamento.detalhes.get('infusao', {}).get('prescricao_id')
        if prescricao_id_nova and prescricao_id_nova != prescricao_id_anterior:
            detalhes = dict(agendamento.detalhes) if agendamento.detalhes else {}
            historico_prescricoes = list(detalhes.get('historico_prescricoes') or [])
            historico_prescricoes.append({
                "data": datetime.now().isoformat(),
                "usuario_id": usuario_id,
                "usuario_nome": usuario_nome,
                "prescricao_id_anterior": prescricao_id_anterior,
                "prescricao_id_nova": prescricao_id_nova,
                "motivo": "Substituição manual"
            })
            detalhes['historico_prescricoes'] = historico_prescricoes
            agendamento.detalhes = detalhes
            flag_modified(agendamento, "detalhes")

            historico_alteracoes.append({
                "data": datetime.now().isoformat(),
                "usuario_id": usuario_id,
                "usuario_nome": usuario_nome,
                "tipo_alteracao": "prescricao",
                "campo": "prescricao_id",
                "valor_antigo": prescricao_id_anterior,
                "valor_novo": prescricao_id_nova,
                "motivo": "Substituição manual"
            })

    if historico_alteracoes:
        agendamento.historico_alteracoes = historico_alteracoes
        flag_modified(agendamento, "historico_alteracoes")

    return prescricao_id_anterior


async def listar_agendamentos(
        agendamento_provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface,
        data_inicio: Optional[date],
        data_fim: Optional[date],
        paciente_id: Optional[str] = None
) -> List[AgendamentoResponse]:
    agendamentos = await agendamento_provider.listar_agendamentos(data_inicio, data_fim, paciente_id)
    if not agendamentos: return []

    prescricao_ids = set()
    for ag in agendamentos:
        if ag.tipo == TipoAgendamento.INFUSAO and ag.detalhes:
            infusao = ag.detalhes.get('infusao')
            if infusao and 'prescricao_id' in infusao: prescricao_ids.add(infusao['prescricao_id'])

    lista_prescricoes = await prescricao_provider.obter_prescricao_multi(list(prescricao_ids))
    mapa_prescricoes = {p.id: p for p in lista_prescricoes}

    response = []
    for ag in agendamentos:
        ag_resp = AgendamentoResponse.model_validate(ag)
        if ag.tipo == 'infusao' and ag.detalhes and 'infusao' in ag.detalhes:
            p_id = ag.detalhes['infusao'].get('prescricao_id')
            if p_id and p_id in mapa_prescricoes:
                prescricao_obj = mapa_prescricoes[p_id]
                p_resp = PrescricaoResponse.model_validate(prescricao_obj)
                ag_resp.prescricao = p_resp
        response.append(ag_resp)

    return response


async def criar_agendamento(
        provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface,
        dados: AgendamentoCreate,
        criado_por_id: str,
        usuario_nome: Optional[str] = None
) -> AgendamentoResponse:
    if dados.tipo == TipoAgendamento.INFUSAO:
        detalhes_inf = dados.detalhes.infusao

        prescricao = await prescricao_provider.obter_prescricao(detalhes_inf.prescricao_id)
        if not prescricao:
            raise HTTPException(status_code=400, detail="Prescrição informada não encontrada.")

        if prescricao.status in ['suspensa', 'cancelada', 'substituida']:
            raise HTTPException(status_code=400, detail="Prescrição indisponível para novos agendamentos.")

        if prescricao.paciente_id != dados.paciente_id:
            raise HTTPException(status_code=400, detail="A prescrição não pertence ao paciente informado.")

        conteudo = prescricao.conteudo
        dias_validos = set()

        if 'blocos' in conteudo:
            for bloco in conteudo['blocos']:
                for item in bloco.get('itens', []):
                    for dia in item.get('dias_do_ciclo', []):
                        dias_validos.add(dia)

        if detalhes_inf.dia_ciclo not in dias_validos:
            dias_str = ", ".join(map(str, sorted(dias_validos)))
            raise HTTPException(
                status_code=400,
                detail=f"Dia do ciclo {detalhes_inf.dia_ciclo} inválido para esta prescrição. Dias válidos com medicação: {dias_str}."
            )

        agendamentos_existentes = await provider.buscar_por_prescricao_e_dia(
            detalhes_inf.prescricao_id,
            detalhes_inf.dia_ciclo
        )

        conflito = [a for a in agendamentos_existentes if a.status not in ['cancelado', 'suspenso', 'remarcado']]

        if conflito:
            data_existente = conflito[0].data.strftime('%d/%m/%Y')
            raise HTTPException(
                status_code=409,
                detail=f"Já existe um agendamento ativo para o Dia {detalhes_inf.dia_ciclo} desta prescrição em {data_existente}. Use a remarcação se necessário."
            )

    novo_id = str(uuid.uuid4())

    agendamento = Agendamento(
        **dados.model_dump(),
        id=novo_id,
        criado_por_id=criado_por_id
    )

    criado = await provider.criar_agendamento(agendamento)

    if dados.tipo == TipoAgendamento.INFUSAO:
        prescricao = await prescricao_provider.obter_prescricao(dados.detalhes.infusao.prescricao_id)
        if prescricao:
            historico_agendamentos = list(prescricao.historico_agendamentos or [])
            historico_agendamentos.append({
                "data": datetime.now().isoformat(),
                "agendamento_id": criado.id,
                "status_agendamento": criado.status,
                "usuario_id": criado_por_id,
                "usuario_nome": usuario_nome,
                "observacoes": "Agendamento criado"
            })
            prescricao.historico_agendamentos = historico_agendamentos
            flag_modified(prescricao, "historico_agendamentos")
            await prescricao_provider.atualizar_prescricao(prescricao)

        await prescricao_controller.recalcular_status_prescricao(
            prescricao_provider,
            provider,
            dados.detalhes.infusao.prescricao_id,
            usuario_id=criado_por_id,
            usuario_nome=usuario_nome
        )

    return AgendamentoResponse.model_validate(criado)


async def atualizar_agendamento(
        provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface,
        agendamento_id: str,
        dados: AgendamentoUpdate,
        usuario_id: Optional[str] = None,
        usuario_nome: Optional[str] = None
) -> AgendamentoResponse:
    agendamento = await provider.obter_agendamento(agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

    update_data = dados.model_dump(exclude_unset=True)
    prescricao_id_anterior = _aplicar_regras_atualizacao(agendamento, update_data)
    atualizado = await provider.atualizar_agendamento(agendamento)

    if agendamento.tipo == TipoAgendamento.INFUSAO.value:
        prescricao_id_atual = agendamento.detalhes.get('infusao', {}).get('prescricao_id') if agendamento.detalhes else None
        if prescricao_id_atual:
            await prescricao_controller.recalcular_status_prescricao(
                prescricao_provider,
                provider,
                prescricao_id_atual,
                usuario_id=usuario_id,
                usuario_nome=usuario_nome
            )

            if 'status' in update_data:
                prescricao = await prescricao_provider.obter_prescricao(prescricao_id_atual)
                if prescricao:
                    historico_agendamentos = list(prescricao.historico_agendamentos or [])
                    historico_agendamentos.append({
                        "data": datetime.now().isoformat(),
                        "agendamento_id": agendamento.id,
                        "status_agendamento": update_data['status'],
                        "usuario_id": usuario_id,
                        "usuario_nome": usuario_nome,
                        "observacoes": "Status do agendamento atualizado"
                    })
                    prescricao.historico_agendamentos = historico_agendamentos
                    flag_modified(prescricao, "historico_agendamentos")
                    await prescricao_provider.atualizar_prescricao(prescricao)

        if prescricao_id_anterior and prescricao_id_anterior != prescricao_id_atual:
            await prescricao_controller.recalcular_status_prescricao(
                prescricao_provider,
                provider,
                prescricao_id_anterior,
                usuario_id=usuario_id,
                usuario_nome=usuario_nome
            )

    return AgendamentoResponse.model_validate(atualizado)


async def atualizar_agendamentos_lote(
        provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface,
        dados_lote: AgendamentoBulkUpdateList,
        usuario_id: Optional[str] = None,
        usuario_nome: Optional[str] = None
) -> List[AgendamentoResponse]:
    ids = [item.id for item in dados_lote.itens]
    agendamentos_existentes = await provider.buscar_por_id_multi(ids)
    mapa_agendamentos = {a.id: a for a in agendamentos_existentes}

    if len(mapa_agendamentos) != len(set(ids)):
        ids_encontrados = set(mapa_agendamentos.keys())
        ids_faltantes = set(ids) - ids_encontrados
        raise HTTPException(
            status_code=404,
            detail=f"Agendamentos não encontrados: {', '.join(ids_faltantes)}"
        )

    processamento_pendente = []
    for item_update in dados_lote.itens:
        agendamento = mapa_agendamentos[item_update.id]
        update_data = item_update.model_dump(exclude={'id'}, exclude_unset=True)
        prescricao_id_anterior = _aplicar_regras_atualizacao(
            agendamento,
            update_data,
            usuario_id=usuario_id,
            usuario_nome=usuario_nome
        )

        processamento_pendente.append({
            "agendamento": agendamento,
            "update_data": update_data,
            "prescricao_id_anterior": prescricao_id_anterior
        })

    atualizados = await provider.atualizar_agendamento_multi(list(mapa_agendamentos.values()))
    for item in processamento_pendente:
        agendamento = item["agendamento"]
        update_data = item["update_data"]
        prescricao_id_anterior = item["prescricao_id_anterior"]

        if agendamento.tipo == TipoAgendamento.INFUSAO.value:
            prescricao_id_atual = agendamento.detalhes.get('infusao', {}).get(
                'prescricao_id') if agendamento.detalhes else None

            if prescricao_id_atual:
                await prescricao_controller.recalcular_status_prescricao(
                    prescricao_provider,
                    provider,
                    prescricao_id_atual,
                    usuario_id=usuario_id,
                    usuario_nome=usuario_nome
                )

                if 'status' in update_data:
                    prescricao = await prescricao_provider.obter_prescricao(prescricao_id_atual)
                    if prescricao:
                        historico_agendamentos = list(prescricao.historico_agendamentos or [])
                        historico_agendamentos.append({
                            "data": datetime.now().isoformat(),
                            "agendamento_id": agendamento.id,
                            "status_agendamento": update_data['status'],
                            "usuario_id": usuario_id,
                            "usuario_nome": usuario_nome,
                            "observacoes": "Status do agendamento atualizado em lote"
                        })
                        prescricao.historico_agendamentos = historico_agendamentos
                        flag_modified(prescricao, "historico_agendamentos")
                        await prescricao_provider.atualizar_prescricao(prescricao)

            if prescricao_id_anterior and prescricao_id_anterior != prescricao_id_atual:
                await prescricao_controller.recalcular_status_prescricao(
                    prescricao_provider,
                    provider,
                    prescricao_id_anterior,
                    usuario_id=usuario_id,
                    usuario_nome=usuario_nome
                )

    return [AgendamentoResponse.model_validate(a) for a in atualizados]


async def trocar_prescricao_agendamento(
        provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface,
        agendamento_id: str,
        dados: AgendamentoPrescricaoUpdate,
        usuario_id: Optional[str] = None,
        usuario_nome: Optional[str] = None
) -> AgendamentoResponse:
    agendamento = await provider.obter_agendamento(agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

    if agendamento.tipo != TipoAgendamento.INFUSAO.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Somente agendamentos de infusão podem trocar prescrição.")

    detalhes = dict(agendamento.detalhes) if agendamento.detalhes else {}
    infusao = detalhes.get('infusao') or {}
    prescricao_id_anterior = infusao.get('prescricao_id')

    if prescricao_id_anterior == dados.prescricao_id:
        return AgendamentoResponse.model_validate(agendamento)

    prescricao_nova = await prescricao_provider.obter_prescricao(dados.prescricao_id)
    if not prescricao_nova:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescrição informada não encontrada")

    if prescricao_nova.status in ['suspensa', 'cancelada', 'substituida']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prescrição indisponível para uso no agendamento")

    if prescricao_nova.paciente_id != agendamento.paciente_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A prescrição não pertence ao paciente do agendamento")

    conteudo = prescricao_nova.conteudo
    dias_validos = set()
    if 'blocos' in conteudo:
        for bloco in conteudo['blocos']:
            for item in bloco.get('itens', []):
                for dia in item.get('dias_do_ciclo', []):
                    dias_validos.add(dia)

    dia_ciclo = infusao.get('dia_ciclo')
    if dia_ciclo and dia_ciclo not in dias_validos:
        dias_str = ", ".join(map(str, sorted(dias_validos)))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dia do ciclo {dia_ciclo} inválido para esta prescrição. Dias válidos com medicação: {dias_str}."
        )

    infusao['prescricao_id'] = prescricao_nova.id
    if prescricao_nova.conteudo and prescricao_nova.conteudo.get('protocolo'):
        infusao['ciclo_atual'] = prescricao_nova.conteudo['protocolo'].get('ciclo_atual')
    detalhes['infusao'] = infusao

    historico_prescricoes = list(detalhes.get('historico_prescricoes') or [])
    historico_prescricoes.append({
        "data": datetime.now().isoformat(),
        "usuario_id": usuario_id,
        "usuario_nome": usuario_nome,
        "prescricao_id_anterior": prescricao_id_anterior,
        "prescricao_id_nova": prescricao_nova.id,
        "motivo": dados.motivo or "Substituição manual"
    })
    detalhes['historico_prescricoes'] = historico_prescricoes

    agendamento.detalhes = detalhes
    flag_modified(agendamento, "detalhes")

    historico_alteracoes = list(agendamento.historico_alteracoes or [])
    historico_alteracoes.append({
        "data": datetime.now().isoformat(),
        "usuario_id": usuario_id,
        "usuario_nome": usuario_nome,
        "tipo_alteracao": "prescricao",
        "campo": "prescricao_id",
        "valor_antigo": prescricao_id_anterior,
        "valor_novo": prescricao_nova.id,
        "motivo": dados.motivo or "Substituição manual"
    })
    agendamento.historico_alteracoes = historico_alteracoes
    flag_modified(agendamento, "historico_alteracoes")

    atualizado = await provider.atualizar_agendamento(agendamento)

    if prescricao_id_anterior:
        prescricao_antiga = await prescricao_provider.obter_prescricao(prescricao_id_anterior)
        if prescricao_antiga:
            historico_agendamentos_antigo = list(prescricao_antiga.historico_agendamentos or [])
            historico_agendamentos_antigo.append({
                "data": datetime.now().isoformat(),
                "agendamento_id": agendamento.id,
                "status_agendamento": agendamento.status,
                "usuario_id": usuario_id,
                "usuario_nome": usuario_nome,
                "observacoes": "Agendamento desvinculado da prescrição"
            })
            prescricao_antiga.historico_agendamentos = historico_agendamentos_antigo
            flag_modified(prescricao_antiga, "historico_agendamentos")
            await prescricao_provider.atualizar_prescricao(prescricao_antiga)

    historico_agendamentos_novo = list(prescricao_nova.historico_agendamentos or [])
    historico_agendamentos_novo.append({
        "data": datetime.now().isoformat(),
        "agendamento_id": agendamento.id,
        "status_agendamento": agendamento.status,
        "usuario_id": usuario_id,
        "usuario_nome": usuario_nome,
        "observacoes": "Agendamento vinculado à prescrição"
    })
    prescricao_nova.historico_agendamentos = historico_agendamentos_novo
    flag_modified(prescricao_nova, "historico_agendamentos")
    await prescricao_provider.atualizar_prescricao(prescricao_nova)

    if prescricao_id_anterior:
        await prescricao_controller.recalcular_status_prescricao(
            prescricao_provider,
            provider,
            prescricao_id_anterior,
            usuario_id=usuario_id,
            usuario_nome=usuario_nome
        )

    await prescricao_controller.recalcular_status_prescricao(
        prescricao_provider,
        provider,
        prescricao_nova.id,
        usuario_id=usuario_id,
        usuario_nome=usuario_nome
    )

    response = AgendamentoResponse.model_validate(atualizado)
    response.prescricao = PrescricaoResponse.model_validate(prescricao_nova)
    return response

