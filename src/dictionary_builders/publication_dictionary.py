import os
import json
import xml.etree.ElementTree as ET

from .base_dictionary_builders import BaseDictionaryBuilder
from tqdm import tqdm

class PublicationDictionaryBuilder(BaseDictionaryBuilder):
    def process_xml_files(self, source_path, output_path):
        all_journals = []

        print(f"Iniciando varredura em: {source_path}")

        # 1. Percorre o diretório e todas as subpastas
        for root, dirs, files in os.walk(source_path):
            with tqdm(total=len(files), desc="Manual Progress") as pbar:
                for file in files:
                    pbar.update(1) 
                    if file.endswith(".xml"):
                        file_path = os.path.join(root, file)
                        
                        try:
                            tree = ET.parse(file_path)
                            xml_root = tree.getroot()

                            for entity in xml_root.findall(".//entity[@type='Publication']"):
                                
                                # Recupera o semanticIdentifier
                                semantic_id_list = entity.findall("semanticIdentifier")
                                for semantic_id_elem in semantic_id_list:
                                    code = semantic_id_elem.text if semantic_id_elem is not None else None
                                    
                                    # Recupera o field onde name="title"
                                    # Usamos [@name='title'] para filtrar diretamente no XML
                                    title_elem = entity.find("./field[@name='title']")
                                    name = title_elem.get("value") if title_elem is not None else None

                                    # Só adiciona se ambos os campos existirem
                                    if code and name:
                                        if str(code).strip().startswith("brcris::"):
                                            all_journals.append({
                                                "code": code.strip(),
                                                "name": name.strip()
                                            })

                        except Exception as e:
                            print(f"Erro ao processar arquivo {file_path}: {e}")


        try:
            with open(f"{output_path}\publication_orcid.json", 'w', encoding='utf-8') as json_file:
                json.dump(
                    all_journals, 
                    json_file, 
                    ensure_ascii=False, 
                    separators=(',', ':') # Remove espaços extras entre chaves e valores
                )
            print(f"\nSucesso! {len(all_journals)} registros salvos em: {output_path}")
        
        except Exception as e:
            print(f"Erro ao salvar o arquivo JSON: {e}")
