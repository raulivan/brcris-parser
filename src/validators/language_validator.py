import json
import os
from typing import Tuple

from .base_validator import BaseValidator, DatasetType

class LanguageValidator(BaseValidator):
    def __init__(self):
        super().__init__()
        
    def load_dataset(self, path:str):
        """
        Lê o arquivo JSON, constrói o mapeamento {name: code} e armazena em self._dataset.
        Garante que a chave (name) seja limpa (strip/lower) para otimizar a busca.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"O arquivo de dados não foi encontrado: {path}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                # O arquivo é um JSON array de objetos
                data = json.load(f)
            
            # Constrói o Dicionário de Mapeamento: {sigla: name}
            mapping: DatasetType = {}
            for item in data:
                sigla = item.get("sigla")
                name = item.get("name_pt")
                
                if name and sigla:
                    cleaned_code = sigla.strip().lower() 
                    mapping[cleaned_code] = name
            
            self._dataset = mapping
            print(f"Idiomas carregadas com sucesso. Total de {len(self._dataset)} entradas.")

        except json.JSONDecodeError:
            raise ValueError("Erro ao decodificar o arquivo JSON de Idiomas. Verifique o formato.")
        except Exception as e:
            raise RuntimeError(f"Erro inesperado no carregamento de dados de Idiomas: {e}")
    
    def is_valid(self, description: str) -> Tuple[bool, str]:
        """
        Recebe uma descrição string e verifica se o nome existe como chave no dataset.
        Retorna o 'code' correspondente se for válido.
        """
        if self._dataset is None:
            raise RuntimeError("O dataset não foi carregado. Execute load_dataset() primeiro.")
            
        if not description:
            return False, None
        
        search_key = description.strip().lower()

        # self._dataset é o dict {name: code}
        found_code = self._dataset.get(search_key)
        
        # Retorna o código (str) ou None
        return found_code is not None, found_code