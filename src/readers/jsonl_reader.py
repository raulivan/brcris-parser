import json
from typing import Generator
from .base_reader import BaseReader

class JSONLReader(BaseReader):
    def read(self, file_path: str) -> Generator[dict, None, None]:
        """
        Lê um arquivo JSONL linha por linha usando um gerador.
        Isso evita carregar todo o arquivo na memória RAM.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as arq:
                for linha in arq:
                    linha = linha.strip()
                    if linha:  # Ignora linhas vazias
                        yield linha
        except FileNotFoundError:
            raise FileNotFoundError(f"Erro: Arquivo {file_path} não encontrado.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar JSON no arquivo {file_path}: {e}")

# import json
# from .base_reader import BaseReader

# class JSONLReader(BaseReader):
#     def read(self, file_path: str) -> list[str]:
#         """Lê um arquivo JSON (contendo uma lista de objetos) e o retorna."""
#         arq = open(file_path, 'rb')
       
#         registros = arq.readlines()
#         return registros