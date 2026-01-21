import os
import json
import csv
import xml.etree.ElementTree as ET

from .base_dictionary_builders import BaseDictionaryBuilder
from tqdm import tqdm

class CourseDictionaryBuilder(BaseDictionaryBuilder):
    def process_xml_files(self, source_path, output_path):
        print(f"Iniciando varredura em: {source_path}")

        with open(f'{output_path}\couse_autoridade.csv', mode='w', newline='', encoding='utf-8') as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(['semanticIdentifier','grau', 'nome'])

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

                            for entity in xml_root.findall(".//entity[@type='Course']"):
                                
                                # Recupera o semanticIdentifier
                                semantic_id_list = entity.findall("semanticIdentifier")
                                for semantic_id_elem in semantic_id_list:
                                    code = semantic_id_elem.text if semantic_id_elem is not None else None       
                                    if code is None or code.strip() == '':
                                        continue

                                    if str(code).strip().startswith("brcris::"):
                                        degree_elem = entity.find("./field[@name='degree']")
                                        grau = degree_elem.get("value") if degree_elem is not None else ''     

                                        name_elem = entity.find("./field[@name='name']")
                                        name = name_elem.get("value") if name_elem is not None else ''                       

                                        with open(f'{output_path}\couse_autoridade.csv', mode='a', newline='', encoding='utf-8') as arquivo:
                                            escritor = csv.writer(arquivo)
                                            escritor.writerow([code,grau,name])

                        except Exception as e:
                            print(f"Erro ao processar arquivo {file_path}: {e}")

