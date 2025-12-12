from .base_mapper import BaseMapper
import hashlib

class XParaAMapper(BaseMapper):
    def transform(self, records: list[dict]) -> list[dict]:
        """
        Converte registros de um CSV de entrada para uma estrutura de dicionário
        pronta para ser convertida em XML pelo XMLWriter.
        """
        transformed_records = []
        for record in records:
            # Lógica para gerar o identifier.brcris (ex: MD5 do nome)
            org_name = record.get("name", "")
            brcris_id_hash = hashlib.md5(org_name.encode('utf-8')).hexdigest()
            brcris_id_value = f"brcris::{brcris_id_hash}"

            # Monta a estrutura que o XMLWriter espera
            new_record = {
                "entity_attribs": {
                    "type": "OrgUnit",
                    # O 'ref' pode ser um ID único da fonte
                    "ref": record.get("id_da_fonte", brcris_id_hash) 
                },
                "fields": [
                    {"name": "identifier.brcris", "preferred": "true", "value": brcris_id_value},
                    {"name": "name", "preferred": "true", "value": org_name, "lang": "POR"}
                    # Adicione outros campos do XML aqui, mapeando a partir do 'record'
                ]
            }
            transformed_records.append(new_record)
        return transformed_records