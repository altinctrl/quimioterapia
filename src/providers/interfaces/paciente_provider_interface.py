from abc import ABC, abstractmethod
from typing import List, Optional

from src.models.paciente import Paciente


class PacienteProviderInterface(ABC):
    @abstractmethod
    async def listar_pacientes(self, termo: Optional[str] = None, ordenacao: str = None, limit: int = 100) -> List[Paciente]:
        pass

    @abstractmethod
    async def obter_paciente_por_codigo(self, codigo: str) -> Optional[Paciente]:
        pass

    @abstractmethod
    async def obter_paciente_por_cpf(self, cpf: str) -> Optional[Paciente]:
        pass

    @abstractmethod
    async def obter_paciente_por_cpf_multi(self, cpfs: List[str]) -> List[Paciente]:
        pass

    @abstractmethod
    async def criar_paciente(self, paciente: Paciente) -> Paciente:
        pass

    @abstractmethod
    async def atualizar_paciente(self, paciente: Paciente) -> Paciente:
        pass
