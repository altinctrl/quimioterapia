import uuid
from datetime import date, datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm.attributes import flag_modified

from src.models.agendamento_model import Agendamento
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.controllers import prescricao_controller
from src.schemas.agendamento_schema import AgendamentoCreate, AgendamentoUpdate, AgendamentoResponse, TipoAgendamento, \
    AgendamentoBulkUpdateList, AgendamentoPrescricaoUpdate, AgendamentoStatusEnum, FarmaciaStatusEnum, \
    AgendamentoRemarcacaoLoteRequest, AgendamentoRemarcacaoRequest
from src.schemas.prescricao_schema import PrescricaoResponse

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
    status_farmacia_anterior = None
    prescricao_id_anterior = None
    if agendamento.tipo == TipoAgendamento.INFUSAO.value and agendamento.detalhes:
        infusao_detalhes = agendamento.detalhes.get('infusao', {})
        prescricao_id_anterior = infusao_detalhes.get('prescricao_id')
        status_farmacia_anterior = infusao_detalhes.get('status_farmacia')
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

    if (agendamento.tipo == TipoAgendamento.INFUSAO.value and
            novo_status == 'aguardando-medicamento' and
            novo_checkin is True):
        detalhes_finais = update_data.get('detalhes')
        if detalhes_finais is None:
            detalhes_finais = dict(agendamento.detalhes) if agendamento.detalhes else {}

        infusao_data = detalhes_finais.get('infusao', {})
        if infusao_data is None: infusao_data = {}
        status_farmacia_atual = infusao_data.get('status_farmacia')
        if status_farmacia_atual == 'agendado':
            infusao_data['status_farmacia'] = 'pendente'
            detalhes_finais['infusao'] = infusao_data
            update_data['detalhes'] = detalhes_finais

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

    if agendamento.tipo == TipoAgendamento.INFUSAO.value and 'detalhes' in update_data:
        status_farmacia_novo = agendamento.detalhes.get('infusao', {}).get('status_farmacia')

        if (status_farmacia_anterior and status_farmacia_novo and
                status_farmacia_anterior != status_farmacia_novo):
            historico_alteracoes.append({
                "data": datetime.now().isoformat(),
                "usuario_id": usuario_id,
                "usuario_nome": usuario_nome,
                "tipo_alteracao": "status_farmacia",
                "campo": "status_farmacia",
                "valor_antigo": status_farmacia_anterior,
                "valor_novo": status_farmacia_novo,
                "motivo": "Alteração automática por check-in/status" if status_farmacia_novo == 'pendente' and status_farmacia_anterior == 'agendado' else None
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


def _calcular_novo_fim(inicio_original: str, fim_original: str, novo_inicio: str) -> str:
    formato = "%H:%M"
    try:
        t_inicio_orig = datetime.strptime(inicio_original, formato)
        t_fim_orig = datetime.strptime(fim_original, formato)
        duracao = t_fim_orig - t_inicio_orig
        t_novo_inicio = datetime.strptime(novo_inicio, formato)
        t_novo_fim = t_novo_inicio + duracao
        return t_novo_fim.strftime(formato)
    except Exception:
        return fim_original


async def _executar_remarcacao_atomica(
        provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface,
        original: Agendamento,
        nova_data: date,
        novo_horario: str,
        motivo: str,
        usuario_id: str,
        usuario_nome: str
) -> Agendamento:
    detalhes_originais = dict(original.detalhes) if original.detalhes else {}
    detalhes_originais['remarcacao'] = {
        "motivo_remarcacao": motivo,
        "nova_data": nova_data.isoformat()
    }

    status_original = original.status
    original.status = AgendamentoStatusEnum.REMARCADO
    original.detalhes = detalhes_originais
    historico = list(original.historico_alteracoes or [])
    historico.append({
        "data": datetime.now().isoformat(),
        "usuario_id": usuario_id,
        "usuario_nome": usuario_nome,
        "tipo_alteracao": "status",
        "valor_antigo": status_original,
        "valor_novo": AgendamentoStatusEnum.REMARCADO,
        "motivo": f"Remarcado para {nova_data}"
    })
    original.historico_alteracoes = historico

    flag_modified(original, "detalhes")
    flag_modified(original, "historico_alteracoes")
    await provider.atualizar_agendamento(original, commit=False)

    novo_horario_fim = _calcular_novo_fim(
        original.horario_inicio,
        original.horario_fim,
        novo_horario
    )
    novos_detalhes = dict(original.detalhes)
    if original.tipo == TipoAgendamento.INFUSAO.value:
        if 'remarcacao' in novos_detalhes: del novos_detalhes['remarcacao']
        if 'cancelamento' in novos_detalhes: del novos_detalhes['cancelamento']
        if 'suspensao' in novos_detalhes: del novos_detalhes['suspensao']
        if 'intercorrencia' in novos_detalhes: del novos_detalhes['intercorrencia']

        infusao = novos_detalhes.get('infusao', {}).copy()
        infusao['status_farmacia'] = FarmaciaStatusEnum.PENDENTE
        infusao['itens_preparados'] = []
        infusao['horario_previsao_entrega'] = None
        novos_detalhes['infusao'] = infusao

    novo_agendamento = Agendamento(
        id=str(uuid.uuid4()),
        paciente_id=original.paciente_id,
        tipo=original.tipo,
        data=nova_data,
        turno='manha' if int(novo_horario.split(':')[0]) < 13 else 'tarde',
        horario_inicio=novo_horario,
        horario_fim=novo_horario_fim,
        checkin=False,
        status=AgendamentoStatusEnum.AGENDADO,
        encaixe=original.encaixe,
        observacoes=f"Remarcado de {original.data.strftime('%d/%m/%Y')}. Motivo: {motivo}",
        tags=original.tags,
        detalhes=novos_detalhes,
        criado_por_id=usuario_id
    )
    criado = await provider.criar_agendamento(novo_agendamento, commit=False)

    if original.tipo == TipoAgendamento.INFUSAO.value:
        prescricao_id = novos_detalhes.get('infusao', {}).get('prescricao_id')
        if prescricao_id:
            prescricao = await prescricao_provider.obter_prescricao(prescricao_id)
            if prescricao:
                hist_presc = list(prescricao.historico_agendamentos or [])
                hist_presc.append({
                    "data": datetime.now().isoformat(),
                    "agendamento_id": original.id,
                    "status_agendamento": AgendamentoStatusEnum.REMARCADO,
                    "usuario_id": usuario_id,
                    "usuario_nome": usuario_nome,
                    "observacoes": f"Remarcado para novo agendamento {criado.id}"
                })
                hist_presc.append({
                    "data": datetime.now().isoformat(),
                    "agendamento_id": criado.id,
                    "status_agendamento": AgendamentoStatusEnum.AGENDADO,
                    "usuario_id": usuario_id,
                    "usuario_nome": usuario_nome,
                    "observacoes": f"Gerado a partir de remarcação de {original.id}"
                })
                prescricao.historico_agendamentos = hist_presc
                flag_modified(prescricao, "historico_agendamentos")
                await prescricao_provider.atualizar_prescricao(prescricao, commit=False)

    return criado


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
    prescricao_id_anterior = _aplicar_regras_atualizacao(agendamento, update_data, usuario_id, usuario_nome)
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


async def remarcar_agendamento(
        provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface,
        agendamento_id: str,
        dados: AgendamentoRemarcacaoRequest,
        usuario_id: str,
        usuario_nome: str
) -> AgendamentoResponse:
    agendamento = await provider.obter_agendamento(agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    horario_final = agendamento.horario_inicio if dados.manter_horario else dados.novo_horario
    if not horario_final:
        raise HTTPException(status_code=400, detail="Horário não fornecido")

    novo_agendamento = await _executar_remarcacao_atomica(
        provider, prescricao_provider, agendamento, dados.nova_data, horario_final,
        dados.motivo, usuario_id, usuario_nome
    )

    response = AgendamentoResponse.model_validate(novo_agendamento)
    await provider.commit()
    return response


async def remarcar_agendamentos_lote(
        provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface,
        dados: AgendamentoRemarcacaoLoteRequest,
        usuario_id: str,
        usuario_nome: str
) -> List[AgendamentoResponse]:
    agendamentos = await provider.buscar_por_id_multi(dados.ids)

    if len(agendamentos) != len(set(dados.ids)):
        raise HTTPException(status_code=404, detail="Alguns agendamentos não foram encontrados")

    novos_agendamentos = []

    for original in agendamentos:
        if original.status == AgendamentoStatusEnum.REMARCADO:
            continue

        horario_final = original.horario_inicio if dados.manter_horario else dados.novo_horario
        if not horario_final:
            horario_final = original.horario_inicio

        novo = await _executar_remarcacao_atomica(
            provider, prescricao_provider, original, dados.nova_data, horario_final,
            dados.motivo, usuario_id, usuario_nome
        )
        novos_agendamentos.append(novo)

    response = [AgendamentoResponse.model_validate(a) for a in novos_agendamentos]
    await provider.commit()
    return response
