from abc import ABC, abstractmethod

class BaseReader(ABC):
    @abstractmethod
    def read(self, file_path: str) -> list[dict]:
        """Lê um arquivo e retorna uma lista de registros (dicionários)."""
        pass