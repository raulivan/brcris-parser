from urllib.parse import urlparse
from typing import Optional

def extrair_id_openalex(url: str) -> Optional[str]:
    """
    Extrai o ID único do OpenAlex (o último segmento do caminho) de uma URL.
    
    Args:
        url: A URL completa do recurso OpenAlex (ex: https://openalex.org/W2741809794).
        
    Returns:
        O ID do OpenAlex como string, ou None se o caminho for inválido.
    """

    parsed_url = urlparse(url)

    path = parsed_url.path
    

    segments = [s for s in path.split('/') if s]
    

    if segments:
        return segments[-1]
    
    return None



# Teste com uma URL mais complexa (com barra final e query params)
url_complexa = "https://openalex.org/W2741809794/?utm_source=api#metadata"
id_complexo = extrair_id_openalex(url_complexa)

print(f"\nURL Complexa: {url_complexa}")
print(f"ID Recuperado: {id_complexo}")