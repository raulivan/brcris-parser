import csv
from .base_reader import BaseReader

class CSVReader(BaseReader):
    def read(self, file_path: str) -> list[dict]:
        """Lê um arquivo CSV e o converte em uma lista de dicionários."""
        with open(file_path, mode='r', encoding='utf-8') as infile:
            return list(csv.DictReader(infile))