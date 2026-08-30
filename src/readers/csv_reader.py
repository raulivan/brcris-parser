import csv
from typing import Generator
from .base_reader import BaseReader

class CSVReader(BaseReader):
    def read(self, file_path: str) -> Generator[list[str], None, None]:
        """Lê um arquivo CSV e o converte em uma lista de dicionários."""

        try:
            with open(file_path, mode='r', encoding='utf-8') as arquivo:
                # Tenta ler para validar o encoding
                arquivo.readline() 
                arquivo.seek(0) # Volta para o início

                leitor = csv.reader(arquivo, delimiter=';')
                for linha in leitor:
                    yield linha
        except UnicodeDecodeError:
            # Se o UTF-8 falhar, ele entra aqui e abre usando latin-1 
            with open(file_path, mode='r', encoding='latin-1') as arquivo:
                leitor = csv.reader(arquivo, delimiter=';')
                for linha in leitor:
                    yield linha