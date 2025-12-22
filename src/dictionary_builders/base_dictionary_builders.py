from abc import ABC, abstractmethod

class BaseDictionaryBuilder(ABC):
    @abstractmethod
    def process_xml_files(self,source_path: str, output_path: str):
        """Gera o dicionario de validação"""
        pass