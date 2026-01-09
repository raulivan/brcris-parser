def map_to_coar(openalex_type: str) -> dict:
    """
    Converte o tipo de publicação do OpenAlex para o padrão COAR.
    Retorna um dicionário com URI e labels.
    """
    if not openalex_type:
        return None

    # Normaliza a entrada (ex: 'Journal-Article' -> 'article')
    # O OpenAlex costuma usar apenas o 'type' simples.
    clean_type = openalex_type.strip().lower()

    # Tenta encontrar no mapeamento
    coar_data = OPENALEX_TO_COAR.get(clean_type)

    if coar_data:
        return coar_data
    
    # Caso não encontre, retorna um tipo genérico "text" do COAR
    return {
        "uri": "http://purl.org/coar/resource_type/c_18cf",
        "label_pt": "texto",
        "label_en": "text"
    }

# --- Exemplo de Uso ---
# tipo_vido_do_openalex = "article"
# coar_result = map_to_coar(tipo_vido_do_openalex)
