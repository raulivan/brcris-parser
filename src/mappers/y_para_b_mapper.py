from .base_mapper import BaseMapper

class YParaBMapper(BaseMapper):
    def transform(self, records: list[dict]) -> list[dict]:
        """Converte registros do formato Y para o formato B."""
        transformed_records = []
        for record in records:
            # Exemplo de lógica de transformação:
            new_record = {
                'identificador': record.get('uuid'),
                'descricao': record.get('details', {}).get('description'),
                'data_criacao': record.get('creation_date')
            }
            transformed_records.append(new_record)
        return transformed_records