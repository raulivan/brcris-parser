import os
import json
import xml.etree.ElementTree as ET

from .base_dictionary_builders import BaseDictionaryBuilder
from tqdm import tqdm

class PersonDictionaryBuilder(BaseDictionaryBuilder):

    def process_xml_files(self, source_path, output_path):
        dicionario_pessoas = {}

        print(f"Iniciando varredura em: {source_path}")

        for root, dirs, files in os.walk(source_path):
            with tqdm(total=len(files), desc="Manual Progress") as pbar:
                for file in files:
                    pbar.update(1) 
                    if file.endswith(".xml"):
                        file_path = os.path.join(root, file)
                        
                        try:
                            tree = ET.parse(file_path)
                            xml_root = tree.getroot()

                            for entity in xml_root.findall(".//entity[@type='Person']"):
                                
                                # Recupera o semanticIdentifier
                                semantic_id_list = entity.findall("semanticIdentifier")
                                for semantic_id_elem in semantic_id_list:
                                    code = semantic_id_elem.text if semantic_id_elem is not None else None
                                    if code == None: 
                                        continue

                                    somente_id = code.split('::')[1]

                                    dicionario_pessoas[somente_id] = code
                        except Exception as e:
                            print(f"Erro ao processar arquivo {file_path}: {e}")

        try:
            with open(f"{output_path}\person_grupos_pesquisa.json", 'w', encoding='utf-8') as json_file:
                json.dump(
                    dicionario_pessoas, 
                    json_file, 
                    ensure_ascii=False, 
                    separators=(',', ':') # Remove espaços extras entre chaves e valores
                )
            print(f"\nSucesso! {len(somente_id)} registros salvos em: {output_path}")
        
        except Exception as e:
            print(f"Erro ao salvar o arquivo JSON: {e}")
