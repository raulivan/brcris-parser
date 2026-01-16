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

