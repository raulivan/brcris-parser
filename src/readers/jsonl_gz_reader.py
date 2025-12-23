import json
import gzip
from .base_reader import BaseReader

class JSONLGZReader(BaseReader):
    def read(self, file_path: str) -> list[str]:
        """Lê um arquivo JSON (contendo uma lista de objetos) e o retorna."""
        with gzip.open(file_path, mode="rt", encoding="utf-8") as f:
            registros = f.readlines()
            return registros
    
            for line in f:
                data = json.loads(line)
                if data['issn_l'] != None or  data['issn'] != None:
                    json_venus.append(data)

            arq = open(file_path, 'rb')
            registros = arq.readlines()
            return registros