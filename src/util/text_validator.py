import re

# Regex
REGEX_URL = re.compile(
    r'([a-zA-Z0-9.-]+(\.[a-zA-Z]{2,})+)'  # Domínio (ex: site.com)
    r'(:\d+)?'  # Porta opcional (:8080)
    r'(/.*)?$'  # Caminho opcional (/rota/arquivo)
)

def validar_url_regex(url):
    if url is None:
        return False
    if not isinstance(url, str):
        return False
    
    return re.match(REGEX_URL, url) is not None

def validar_titulo(titulo) -> bool:
    """
    Método que valida se um título é cosniderado válidos
    
    :param titulo: titulo da publicação
    """
    if titulo is None:
        return False
    
    if titulo == None:
        return False
    
    titulo = str(titulo).strip()
    
    if titulo == '':
        return False
    
    tokens = titulo.split(" ")
    
    token_validos_count = 0

    for t in tokens:
        if len(t.strip()) > 0:
            token_validos_count += 1
        if token_validos_count > 3:
            break   

    return token_validos_count > 0

