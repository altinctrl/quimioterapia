from fastapi import APIRouter, Depends
from typing import List

from ..controllers import poltrona_controller
from ..dependencies import get_poltrona_provider
from ..providers.interfaces.poltrona_provider_interface import PoltronaProviderInterface
from ..schemas.poltrona import PoltronaResponse
from ..auth.auth import auth_handler

STRATEGY = "POSTGRES"

router = APIRouter(
    prefix="/api/poltronas",
    tags=["Poltronas"],
    dependencies=[Depends(auth_handler.decode_token)]
)

@router.get("", response_model=List[PoltronaResponse])
async def listar(
    provider: PoltronaProviderInterface = Depends(get_poltrona_provider(STRATEGY))
):
    return await poltrona_controller.listar_poltronas(provider)