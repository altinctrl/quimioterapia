import io
import os
from collections import defaultdict
from datetime import datetime, date

from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.providers.interfaces.equipe_provider_interface import EquipeProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.schemas.agendamento import AgendamentoResponse, TipoAgendamento, TipoConsulta, AgendamentoStatusEnum, \
    TipoIntercorrencia, MotivoSuspensao, FarmaciaStatusEnum, MAPA_PROCEDIMENTOS, MAPA_MOTIVOS_SUSPENSAO
from src.schemas.equipe import EscalaPlantaoResponse, AusenciaProfissionalResponse
from src.schemas.protocolo import TipoTerapiaEnum


def calcular_duracao_horas(inicio_str: str, fim_str: str) -> float:
    try:
        fmt = "%H:%M"
        t1 = datetime.strptime(inicio_str, fmt)
        t2 = datetime.strptime(fim_str, fmt)
        delta = t2 - t1
        return delta.total_seconds() / 3600
    except:
        return 0.0


async def gerar_relatorio_fim_plantao(
        data_inicio: date,
        data_fim: date,
        agendamento_provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface,
        equipe_provider: EquipeProviderInterface
):
    agendamentos_orm = await agendamento_provider.listar_agendamentos(data_inicio=data_inicio, data_fim=data_fim)
    agendamentos = [AgendamentoResponse.model_validate(ag) for ag in agendamentos_orm]
    escala = []
    if data_inicio == data_fim:
        escala_orm = await equipe_provider.listar_escala_dia(data_inicio)
        escala = [EscalaPlantaoResponse.model_validate(item) for item in escala_orm]
    ausencias_orm = await equipe_provider.listar_ausencias_periodo(data_inicio=data_inicio, data_fim=data_fim)
    ausencias = [AusenciaProfissionalResponse.model_validate(a) for a in ausencias_orm]

    prescricao_ids = set()
    for ag in agendamentos:
        if ag.tipo == TipoAgendamento.INFUSAO and ag.detalhes.infusao:
            prescricao_ids.add(ag.detalhes.infusao.prescricao_id)
    mapa_prescricoes = {}
    if prescricao_ids:
        lista_prescricoes = await prescricao_provider.obter_prescricao_multi(list(prescricao_ids))
        mapa_prescricoes = {p.id: p for p in lista_prescricoes}

    stats = {
        "agendados": len(agendamentos),
        "encaixes": 0,
        "consultas_triagem": 0,
        "consultas_navegacao": 0,
        "ausentes": 0,
        "total_infusoes": 0,
        "duracao_maior_4h": 0,
        "duracao_2h_4h": 0,
        "duracao_ate_2h": 0,
        "rituximabe_especial": 0,
        "hormonioterapia": 0,
        "imuno_alvo": 0,
        "zometa": 0,
        "procedimentos": defaultdict(int),
        "suspensoes_total": 0,
        "motivos_suspensao": defaultdict(int),
        "derramamentos": 0,
        "hipersensibilidade": 0,
        "extravasamentos": 0,
        "derramamento_drogas": set(),
        "hipersensibilidade_drogas": set(),
        "extravasamento_drogas": set(),
        "suspensao_med_drogas": set(),
        "vigihosp_realizado": False,
        "internamentos": 0,
        "remarcados": 0
    }

    for ag in agendamentos:
        if ag.encaixe: stats["encaixes"] += 1

        if ag.status in [AgendamentoStatusEnum.SUSPENSO]:
            stats["suspensoes_total"] += 1
            if ag.detalhes.suspensao:
                raw_motivo = ag.detalhes.suspensao.motivo_suspensao
                motivo = MAPA_MOTIVOS_SUSPENSAO.get(raw_motivo, raw_motivo)
                stats["motivos_suspensao"][motivo] += 1
                if motivo == MotivoSuspensao.FALTA_MEDICACAO and ag.detalhes.suspensao.medicamento_falta:
                    stats["suspensao_med_drogas"].add(ag.detalhes.suspensao.medicamento_falta)
        elif ag.status == AgendamentoStatusEnum.REMARCADO:
            stats["remarcados"] += 1
        elif ag.status == AgendamentoStatusEnum.INTERNADO:
            stats["internamentos"] += 1
        elif ag.status == AgendamentoStatusEnum.INTERCORRENCIA and ag.detalhes.intercorrencia:
            tipo = ag.detalhes.intercorrencia.tipo_intercorrencia
            med = ag.detalhes.intercorrencia.medicamento_intercorrencia
            if tipo == TipoIntercorrencia.DERRAMAMENTO:
                stats["derramamentos"] += 1
                if med: stats["derramamento_drogas"].add(med)
            elif tipo == TipoIntercorrencia.HIPERSENSIBILIDADE:
                stats["hipersensibilidade"] += 1
                if med: stats["hipersensibilidade_drogas"].add(med)
                if ag.detalhes.intercorrencia.vigihosp:
                    stats["vigihosp_realizado"] = True
            elif tipo == TipoIntercorrencia.EXTRAVASAMENTO:
                stats["extravasamentos"] += 1
                if med: stats["extravasamento_drogas"].add(med)

        if ag.tipo == TipoAgendamento.CONSULTA and ag.detalhes.consulta:
            if ag.detalhes.consulta.tipo_consulta == TipoConsulta.TRIAGEM:
                stats["consultas_triagem"] += 1
            elif ag.detalhes.consulta.tipo_consulta == TipoConsulta.NAVEGACAO:
                stats["consultas_navegacao"] += 1
        elif ag.tipo == TipoAgendamento.PROCEDIMENTO and ag.detalhes.procedimento:
            raw_proc = ag.detalhes.procedimento.tipo_procedimento
            procedimento = MAPA_PROCEDIMENTOS.get(raw_proc, raw_proc)
            stats["procedimentos"][procedimento] += 1
        elif ag.tipo == TipoAgendamento.INFUSAO:
            if ag.checkin and ag.status in [AgendamentoStatusEnum.CONCLUIDO, AgendamentoStatusEnum.INTERCORRENCIA]:
                stats["total_infusoes"] += 1

                duracao = calcular_duracao_horas(ag.horario_inicio, ag.horario_fim)
                if duracao > 4:
                    stats["duracao_maior_4h"] += 1
                elif duracao >= 2:
                    stats["duracao_2h_4h"] += 1
                else:
                    stats["duracao_ate_2h"] += 1

                presc_id = ag.detalhes.infusao.prescricao_id if ag.detalhes.infusao else None
                prescricao = mapa_prescricoes.get(presc_id)

                if prescricao:
                    conteudo = prescricao.conteudo
                    if not isinstance(conteudo, dict): conteudo = {}
                    protocolo = conteudo.get('protocolo', {})
                    tipo_terapia = protocolo.get('tipo_terapia', '').lower()

                    if tipo_terapia == TipoTerapiaEnum.HORMONIOTERAPIA:
                        stats["hormonioterapia"] += 1
                    if tipo_terapia in [TipoTerapiaEnum.IMUNOTERAPIA,
                                        TipoTerapiaEnum.TERAPIA_ALVO,
                                        TipoTerapiaEnum.ANTICORPO_MONOCLONAL]:
                        stats["imuno_alvo"] += 1

                    if 'blocos' in conteudo and isinstance(conteudo['blocos'], list):
                        for bloco in conteudo['blocos']:
                            for item in bloco.get('itens', []):
                                nome_med = item.get('medicamento', '').lower()
                                if 'zometa' in nome_med or 'acido zoledronico' in nome_med:
                                    stats["zometa"] += 1
                                if 'rituximabe' in nome_med:
                                    stats["rituximabe_especial"] += 1

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('relatorio_fim_plantao.html')

    html_content = template.render(
        data_formatada=data_inicio.strftime(
            "%d/%m/%Y") if data_inicio == data_fim else f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
        data_hora_geracao=datetime.now().strftime("%d/%m/%Y às %H:%M"),
        equipe=escala,
        ausencias=ausencias,
        stats=stats
    )

    pdf_file = HTML(string=html_content).write_pdf()

    nome_arquivo = f"plantao_{data_inicio}" if data_inicio == data_fim else f"plantao_{data_inicio}_{data_fim}"
    return StreamingResponse(
        io.BytesIO(pdf_file),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={nome_arquivo}.pdf"}
    )


async def gerar_relatorio_medicacoes(
        data_inicio: date,
        data_fim: date,
        agendamento_provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface
):
    agendamentos_orm = await agendamento_provider.listar_agendamentos(data_inicio=data_inicio, data_fim=data_fim)
    agendamentos = [AgendamentoResponse.model_validate(ag) for ag in agendamentos_orm]

    prescricao_ids = set()
    for ag in agendamentos:
        if ag.tipo == TipoAgendamento.INFUSAO and ag.detalhes.infusao:
            prescricao_ids.add(ag.detalhes.infusao.prescricao_id)

    mapa_prescricoes = {}
    if prescricao_ids:
        lista_prescricoes = await prescricao_provider.obter_prescricao_multi(list(prescricao_ids))
        mapa_prescricoes = {p.id: p for p in lista_prescricoes}

    resumo_meds = {}

    for ag in agendamentos:
        if ag.tipo != TipoAgendamento.INFUSAO: continue
        if not ag.detalhes.infusao: continue

        status_farmacia = ag.detalhes.infusao.status_farmacia
        foi_enviado = (status_farmacia == FarmaciaStatusEnum.ENVIADO and ag.checkin)
        eh_ausente = (not ag.checkin)

        nome_paciente = ag.paciente.nome if ag.paciente else "Desconhecido"

        p_id = ag.detalhes.infusao.prescricao_id
        prescricao = mapa_prescricoes.get(p_id)
        if not prescricao: continue

        dia_ciclo_agendamento = ag.detalhes.infusao.dia_ciclo
        conteudo = prescricao.conteudo if isinstance(prescricao.conteudo, dict) else {}

        if 'blocos' in conteudo and isinstance(conteudo['blocos'], list):
            for bloco in conteudo['blocos']:
                for item in bloco.get('itens', []):
                    dias_item = item.get('dias_do_ciclo', [])
                    if dia_ciclo_agendamento in dias_item:
                        nome = item.get('medicamento')
                        unidade_original = item.get('unidade', '')

                        if unidade_original.upper() == 'AUC':
                            unidade = 'mg'
                        elif '/' in unidade_original:
                            unidade = unidade_original.split('/')[0]
                        else:
                            unidade = unidade_original
                        raw_dose = item.get('dose_final')

                        try:
                            if raw_dose is None or raw_dose == "":
                                dose = 0.0
                            else:
                                if isinstance(raw_dose, str):
                                    raw_dose = raw_dose.replace(',', '.')
                                dose = float(raw_dose)
                        except (ValueError, TypeError):
                            dose = 0.0

                        chave = f"{nome} - {unidade}"
                        if chave not in resumo_meds:
                            resumo_meds[chave] = {
                                "nome": nome,
                                "unidade": unidade,
                                "qtd_prescrito": 0.0,
                                "qtd_enviado": 0.0,
                                "qtd_ausente": 0.0,
                                "lista_enviados": [],
                                "lista_ausentes": []
                            }

                        resumo_meds[chave]["qtd_prescrito"] = round(resumo_meds[chave]["qtd_prescrito"] + dose, 2)

                        info_paciente = {
                            "nome": nome_paciente,
                            "dose": round(dose, 2)
                        }

                        if foi_enviado:
                            resumo_meds[chave]["lista_enviados"].append(info_paciente)
                            resumo_meds[chave]["qtd_enviado"] = round(resumo_meds[chave]["qtd_enviado"] + dose, 2)

                        if eh_ausente:
                            resumo_meds[chave]["lista_ausentes"].append(info_paciente)
                            resumo_meds[chave]["qtd_ausente"] = round(resumo_meds[chave]["qtd_ausente"] + dose, 2)

    lista_medicacoes = sorted(resumo_meds.values(), key=lambda x: x['nome'])

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('relatorio_medicacoes.html')

    html_content = template.render(
        data_inicio=data_inicio.strftime("%d/%m/%Y"),
        data_fim=data_fim.strftime("%d/%m/%Y"),
        data_hora_geracao=datetime.now().strftime("%d/%m/%Y às %H:%M"),
        medicacoes=lista_medicacoes
    )

    pdf_file = HTML(string=html_content).write_pdf()

    return StreamingResponse(
        io.BytesIO(pdf_file),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=medicacoes_{data_inicio}.pdf"}
    )
