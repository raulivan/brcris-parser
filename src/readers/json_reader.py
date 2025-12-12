import json
from .base_reader import BaseReader

class JSONReader(BaseReader):
    def read(self, file_path: str) -> list[dict]:
        """Lê um arquivo JSON (contendo uma lista de objetos) e o retorna."""
        with open(file_path, mode='r', encoding='utf-8') as infile:
            return json.load(infile)