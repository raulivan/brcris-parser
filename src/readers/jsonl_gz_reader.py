import json
from .base_reader import BaseReader

class JSONLReader(BaseReader):
    def read(self, file_path: str) -> list[str]:
        """Lê um arquivo JSON (contendo uma lista de objetos) e o retorna."""
        arq = open(file_path, 'rb')
        registros = arq.readlines()
        return registros