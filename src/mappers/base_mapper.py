from typing import List, Optional
import uuid
from abc import ABC, abstractmethod

from validators.base_validator import BaseValidator
from util.unique_identifier_generator import uuid_based_identifier_generator

class BaseMapper(ABC):
    @abstractmethod
    def transform(self, records: list[dict], validators: List[BaseValidator] = []) -> list[dict]:
        """Transforma uma lista de registros de origem para o formato de destino."""
        pass
    
    def creat_ref_identifier(self) -> str:
        return uuid_based_identifier_generator()
    
    def get_field_value(self, record: dict, field_name: str) -> str:
        if record == None:
            return None
        
        if field_name == None:
            return None
        
        value = record.get(field_name, None)
        if field_name is str:
            if value == '':
                return None
            
            if str(valur).strip().lower() == 'null':
                return None
            
        return value
    
    def has_value(self, node):
        # 1. Checagem contra None (Está correto: 'is' para singletons)
        if node is None:
            return False
        
        # 2. Checagem para Strings (CORRIGIDO com isinstance)
        if isinstance(node, str):
            # Converte para string e limpa espaços antes de checar 'null' ou vazio
            stripped_node = node.strip()
            
            # O teste 'str(node)' é desnecessário aqui, pois node já é str
            if stripped_node.lower() == 'null':
                return False
            
            if stripped_node == '':
                return False
        
        # 3. Checagem para Listas (CORRIGIDO com isinstance)
        if isinstance(node, list):
            # A verificação 'if len(node) == 0' é equivalente a 'if not node'
            if not node:
                return False
            
        # 4. Checagem para Dicionários (CORRIGIDO com isinstance)
        if isinstance(node, dict):
            # A verificação 'if len(node) == 0' é equivalente a 'if not node'
            if not node:
                return False
                
        # Se passou por todas as verificações e não retornou False, tem valor.
        return True
    
    def retrieve_validator_by_type(self, validators: List[BaseValidator], target_type: type) -> Optional[BaseValidator]:
        """
        Busca e retorna a primeira instância de um tipo específico na lista de validadores.
        
        Args:
            validators: A lista de instâncias BaseValidator.
            target_type: A classe (o tipo) que se deseja buscar (ex: OrgUnitValidator).
            
        Returns:
            A instância do validador se encontrada, ou None.
        """
        
        # Filtra a lista, mantendo apenas os objetos que a instância é do tipo 'target_type'.
        encontrados = [
            validator 
            for validator in validators 
            if isinstance(validator, target_type)
        ]
        
        return encontrados[0] if encontrados else None