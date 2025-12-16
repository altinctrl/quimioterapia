import io
import os
import uuid
from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from src.models.prescricao import Prescricao, ItemPrescricao
from src.providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.schemas.prescricao import PrescricaoCreate, PrescricaoResponse


async def listar_prescricoes(provider: PrescricaoProviderInterface, paciente_id: str) -> List[PrescricaoResponse]:
    prescricoes = await provider.listar_por_paciente(paciente_id)
    response = []
    for p in prescricoes:
        resp = PrescricaoResponse.model_validate(p)
        resp.protocolo = p.protocolo_nome_snapshot

        qt_items = [i for i in p.itens if i.tipo == 'qt']
        pre_items = [i for i in p.itens if i.tipo == 'pre']
        pos_items = [i for i in p.itens if i.tipo == 'pos']

        response_dict = resp.model_dump()
        response_dict['qt'] = qt_items
        response_dict['medicamentos'] = pre_items
        response_dict['pos_medicacoes'] = pos_items

        response.append(PrescricaoResponse(**response_dict))
    return response


async def criar_prescricao(provider: PrescricaoProviderInterface, dados: PrescricaoCreate) -> PrescricaoResponse:
    novo_id = str(uuid.uuid4())
    prescricao_dict = dados.model_dump(exclude={"medicamentos", "qt", "pos_medicacoes", "hora_assinatura"})

    prescricao = Prescricao(**prescricao_dict, id=novo_id)

    itens_map = {"qt": dados.qt, "pre": dados.medicamentos, "pos": dados.pos_medicacoes}

    for tipo, lista in itens_map.items():
        for item in lista:
            novo_item = ItemPrescricao(**item.model_dump(), tipo=tipo)
            prescricao.itens.append(novo_item)

    criado = await provider.criar_prescricao(prescricao)

    resp = PrescricaoResponse.model_validate(criado)
    resp_dict = resp.model_dump()
    resp_dict['qt'] = [i for i in criado.itens if i.tipo == 'qt']
    resp_dict['medicamentos'] = [i for i in criado.itens if i.tipo == 'pre']
    resp_dict['pos_medicacoes'] = [i for i in criado.itens if i.tipo == 'pos']

    return PrescricaoResponse(**resp_dict)


async def gerar_pdf_prescricao(prescricao_id: str, prescricao_provider: PrescricaoProviderInterface,
        paciente_provider: PacienteProviderInterface):
    prescricao = await prescricao_provider.obter_prescricao(prescricao_id)
    if not prescricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescrição não encontrada")

    paciente = await paciente_provider.obter_paciente_por_codigo(prescricao.paciente_id)

    qt_items = [i for i in prescricao.itens if i.tipo == 'qt']
    pre_items = [i for i in prescricao.itens if i.tipo == 'pre']
    pos_items = [i for i in prescricao.itens if i.tipo == 'pos']

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, 'templates')

    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('prescricao_pdf.html')

    html_content = template.render(prescricao=prescricao, paciente=paciente, qt_items=qt_items, pre_items=pre_items,
        pos_items=pos_items, agora=datetime.now().strftime("%d/%m/%Y %H:%M"))

    pdf_file = HTML(string=html_content).write_pdf()

    return StreamingResponse(io.BytesIO(pdf_file), media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=prescricao_{prescricao_id}.pdf"})
