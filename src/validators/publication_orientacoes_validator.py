import json
import os
from typing import Dict, List, Tuple

from .base_validator import BaseValidator, DatasetType

class PublicationOrientacoesValidator(BaseValidator):
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
                data: List[Dict[str, str]] = json.load(f)
            
            # Constrói o Dicionário de Mapeamento: {name_limpo: code}
            mapping: DatasetType = {}
            for item in data:
                name = item.get("name")
                code = item.get("code")
                
                if name and code:
                    cleaned_code = code.strip().lower() 
                    mapping[cleaned_code] = name
            
            self._dataset = mapping
            print(f"Journal carregadas com sucesso. Total de {len(self._dataset)} entradas.")

        except json.JSONDecodeError:
            raise ValueError("Erro ao decodificar o arquivo JSON de Journal. Verifique o formato.")
        except Exception as e:
            raise RuntimeError(f"Erro inesperado no carregamento de dados de Journal: {e}")
    
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