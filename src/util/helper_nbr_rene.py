import re
from typing import Optional
import zlib, hashlib


def hash(texto: str,tamanho=15) -> str:
    """
    Gera uma hash SHA-256 a partir de uma string.
    """
    return hashlib.sha256(texto.encode()).hexdigest()[:tamanho]


def crc32_hex(s: str, enc='utf-8') -> str:
    b = s.encode(enc)
    return f"{zlib.crc32(b) & 0xFFFFFFFF:08x}"  # máscara p/ 32 bits

def adler32_hex(s: str, enc='utf-8') -> str:
    b = s.encode(enc)
    return f"{zlib.adler32(b) & 0xFFFFFFFF:08x}"

# Palavras que devem ficar em minúsculas (exceto se forem a 1ª palavra)
STOPWORDS = {
    # PT
    "de",
    "da",
    "do",
    "das",
    "dos",
    "e",
    "em",
    "na",
    "no",
    "nas",
    "nos",
    "a",
    "o",
    "as",
    "os",
    "para",
    "por",
    "per",
    "com",
    "sem",
    "entre",
    "sobre",
    # EN
    "of",
    "the",
    "and",
    "for",
    "to",
    "in",
    "on",
    "at",
    "by",
    "from",
    "vs",
    # ES/IT/FR/DE (comuns em nomes corporativos)
    "y",
    "del",
    "di",
    "della",
    "delle",
    "la",
    "le",
    "les",
    "du",
    "des",
    "von",
    "van"
}

def removeStopWords(n):
    words = n.split(" ")
    words = [w for w in words if w.lower() not in STOPWORDS]
    return " ".join(words)

def nbr_author(n):
    n = n.replace("'","´")
    n2 = n
    if (n.find(';') > 0):
        p = n.find(';')
        n2 = n[0:p].strip()

    if (n2.find(',') > 0):
        p = n2.find(',')
        n2 = n2[p+1:].strip() + ' ' + n2[0:p].strip()
    n2.strip()
    return n2

def nbr_subject(n):
    n2 = n.lower()
    nA = n2[0:1].upper()
    n2 = nA+n2[1:]
    return n2


def nbr_corporate(n: Optional[str], rows=None) -> str:
    """
    Title case para nomes corporativos:
    - Primeira letra de cada palavra em maiúscula, restante minúscula.
    - Preposições/artigos em STOPWORDS ficam em minúsculas (exceto a 1ª palavra).
    - Normaliza espaços e quebras de linha.
    - Preserva separadores '-' e '/' aplicando a mesma regra em cada parte.
    """
    if n is None:
        return ""

    n = n.replace("'","´")

    ################# Separador " - "
    if (n.find(' -') > 0):
        nn = n.find(' -')
        n = n[:nn]

    ################# Remoções
    n = n.replace('(','( ')
    n = n.replace('/',' ')

    ################# Abreviaturas
    n = n.replace('Univ.','Universidade')
    n = n.replace('Educ.','Educação')

    ################# Exessões
    n = n.replace('Inc.','Inc#')
    n = n.replace('Ltda.','Ltda#')

    n = n.replace('.',' ')

    ################# Exessões
    n = n.replace('Inc#','Inc.')
    n = n.replace('Ltda#','Ltda.')

    # Normaliza espaços e quebras de linha
    s = str(n).replace("\r", " ").replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip().lower()

    if not s:
        return s

    def _title_token(token: str, is_first: bool) -> str:
        # Divide em partes preservando '-' e '/'
        parts = re.split(r"([-/])", token)
        out = []
        for p in parts:
            if p in {"-", "/"} or p == "":
                out.append(p)
                continue
            # stopwords ficam minúsculas (se não for a primeira palavra)
            if (p in STOPWORDS) and not is_first:
                out.append(p)
            else:
                out.append(p[:1].upper() + p[1:].lower())
        return "".join(out)


    words = s.split(" ")
    titled = [_title_token(w, i == 0) for i, w in enumerate(words)]
    s = " ".join(titled)
    s = s.replace('( ', '(')
    s = s.replace(' )', ')')
    s = s.replace('S.a', 'S.A.')

    s = s.replace('Usp', 'Universidade de São Paulo')
    return s

def nbr_title(n,rows=[]):
    n2 = n.lower()
    n2 = n2.replace(chr(13),' ')
    n2 = n2.replace(chr(10),' ')
    n2 = n2.replace('  ',' ')
    n2 = n2.replace(chr(13),' ')
    n2 = ' '+n2+' '

    for r in rows:
        n2 = n2.replace(' '+r[1]+' ',' '+r[2]+' ')
        n2 = n2.replace(' '+r[1]+',',' '+r[2]+',')
        n2 = n2.replace(' '+r[1]+':',' '+r[2]+':')
        n2 = n2.replace(' '+r[1]+'.',' '+r[2]+'.')
        n2 = n2.replace(' '+r[1]+')',' '+r[2]+')')
        n2 = n2.replace('('+r[1]+' ','('+r[2]+' ')
        n2 = n2.replace('('+r[1]+')','('+r[2]+')')
    n2 = n2.strip()
    nA = n2[0:1].upper()
    n2 = nA+n2[1:]
    return n2
