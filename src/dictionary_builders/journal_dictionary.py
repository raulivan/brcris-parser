import os
import json
import xml.etree.ElementTree as ET

from .base_dictionary_builders import BaseDictionaryBuilder
from tqdm import tqdm

class JournalDictionaryBuilder(BaseDictionaryBuilder):
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
                            # 2. Carrega e analisa o arquivo XML
                            tree = ET.parse(file_path)
                            xml_root = tree.getroot()

                            # 3. Busca todos os elementos <entity> com type="Journal"
                            # O XPath './/entity[@type="Journal"]' encontra qualquer entity Journal no arquivo
                            for entity in xml_root.findall(".//entity[@type='Journal']"):
                                
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
                                        if str(code).strip().startswith("issn::"):
                                            all_journals.append({
                                                "code": code.strip(),
                                                "name": name.strip()
                                            })

                        except Exception as e:
                            print(f"Erro ao processar arquivo {file_path}: {e}")

        # 4. Salva o arquivo JSON
        # Para remover indentação e quebras de linha (minified), 
        # não passamos o argumento 'indent' e definimos 'separators' compactos.
        try:
            with open(f"{output_path}\journals.json", 'w', encoding='utf-8') as json_file:
                json.dump(
                    all_journals, 
                    json_file, 
                    ensure_ascii=False, 
                    separators=(',', ':') # Remove espaços extras entre chaves e valores
                )
            print(f"\nSucesso! {len(all_journals)} registros salvos em: {output_path}")
        
        except Exception as e:
            print(f"Erro ao salvar o arquivo JSON: {e}")
