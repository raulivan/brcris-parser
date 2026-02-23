import zipfile
from typing import Generator
from .base_reader import BaseReader


class ZipXMLReader(BaseReader):
    def read(self, file_path: str) -> Generator[str, None, None]:
        """
        Abre um arquivo .zip, itera sobre todos os arquivos internos,
        e retorna (yield) o conteúdo de cada arquivo .xml encontrado como string.
        """
        try:
            # Abre o arquivo ZIP no modo de leitura ('r')
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                
                # zip_ref.infolist() retorna informações de cada arquivo lá dentro
                for file_info in zip_ref.infolist():
                    
                    # Ignora diretórios e arquivos que não sejam XML
                    if file_info.is_dir() or not file_info.filename.lower().endswith('.xml'):
                        continue
                    
                    try:
                        # Abre especificamente o arquivo XML atual de dentro do ZIP
                        with zip_ref.open(file_info) as xml_file:
                            xml_content = xml_file.read().decode('ISO-8859-1')
                            
                            # tree = ET.parse(file_path)
                           
                            
                            yield xml_content
                            
                    except UnicodeDecodeError:
                        print(f"Erro de codificação ao ler {file_info.filename}. Talvez não seja UTF-8.")
                        continue
                    except Exception as e:
                        print(f"Erro ao processar o arquivo {file_info.filename} no zip {file_path}: {e}")
                        continue
                        
        except zipfile.BadZipFile:
            raise ValueError(f"O arquivo {file_path} não é um arquivo ZIP válido ou está corrompido.")
        except Exception as e:
            raise ValueError(f"Erro ao abrir arquivo ZIP {file_path}: {e}")