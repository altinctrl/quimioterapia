from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from src.models.equipe import Profissional, EscalaPlantao, AusenciaProfissional
from src.schemas.equipe import ProfissionalCreate, EscalaPlantaoCreate, AusenciaProfissionalCreate


class EquipeProviderInterface(ABC):

    @abstractmethod
    async def buscar_profissional_por_username(self, username: str) -> Optional[Profissional]:
        pass

    @abstractmethod
    async def listar_profissionais(self, apenas_ativos: bool = True) -> List[Profissional]:
        pass

    @abstractmethod
    async def atualizar_profissional(self, username: str, dados: ProfissionalCreate) -> Optional[Profissional]:
        pass

    @abstractmethod
    async def adicionar_item_escala(self, escala: EscalaPlantaoCreate) -> EscalaPlantao:
        pass

    @abstractmethod
    async def listar_escala_dia(self, data: date) -> List[EscalaPlantao]:
        pass

    @abstractmethod
    async def remover_item_escala(self, item_id: str) -> bool:
        pass

    @abstractmethod
    async def registrar_ausencia(self, ausencia: AusenciaProfissionalCreate) -> AusenciaProfissional:
        pass

    @abstractmethod
    async def listar_ausencias_periodo(self, data_inicio: date, data_fim: date) -> List[AusenciaProfissional]:
        pass

    @abstractmethod
    async def remover_ausencia(self, ausencia_id: str) -> bool:
        pass

    @abstractmethod
    async def promover_usuario_a_profissional(self, dados) -> Optional[Profissional]:
        pass
