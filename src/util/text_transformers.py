import re
from unicodedata import normalize

# Lista de palavras curtas que geralmente não são capitalizadas no Title Case
PALAVRAS_DE_EXCECAO = {
    'de', 'do', 'da', 'dos', 'das', 'e', 'em', 'para', 'por', 'o', 'a', 'os', 'as', 'com', 'sem'
}

# begin Usado na função replaceHtmlChars *****
html_chars = {'&nbsp;': ' ', '&acute;': '´', '&Alpha;': 'Α', '&alpha;': 'α', '&amp;': '&', '&and;': '∧', '&ang;': '∠', '&asymp;': '≈', '&bdquo;': '„', '&Beta;': 'Β', '&beta;': 'β', '&brvbar;': '¦', '&bull;': '•', '&cap;': '∩', '&cedil;': '¸', '&cent;': '¢', '&Chi;': 'Χ', '&chi;': 'χ', '&circ;': 'ˆ', '&clubs;': '♣', '&cong;': '≅', '&copy;': '©', '&crarr;': '↵', '&cup;': '∪', '&curren;': '¤', '&dagger;': '†', '&Dagger;': '‡', '&darr;': '↓', '&deg;': '°', '&Delta;': 'Δ', '&delta;': 'δ', '&diams;': '♦', '&divide;': '÷', '&empty;': '∅', '&emsp;': '\u2003', '&ensp;': '\u2002', '&Epsilon;': 'Ε', '&epsilon;': 'ε', '&equiv;': '≡', '&Eta;': 'Η', '&eta;': 'η', '&euro;': '€', '&exist;': '∃', '&fnof;': 'ƒ', '&forall;': '∀', '&frac12;': '½', '&frac14;': '¼', '&frac34;': '¾', '&Gamma;': 'Γ', '&gamma;': 'γ', '&ge;': '≥', '&gt;': '>', '&harr;': '↔', '&hearts;': '♥', '&hellip;': '…', '&iexcl;': '¡', '&infin;': '∞', '&int;': '∫', '&Iota;': 'Ι', '&iota;': 'ι', '&iquest;': '¿', '&isin;': '∈', '&Kappa;': 'Κ', '&kappa;': 'κ', '&Lambda;': 'Λ', '&lambda;': 'λ', '&laquo;': '«', '&larr;': '←', '&lceil;': '⌈', '&ldquo;': '“', '&le;': '≤', '&lfloor;': '⌊', '&lowast;': '∗', '&loz;': '◊', '&lrm;': '\u200e', '&lsaquo;': '‹', '&lsquo;': '‘', '&lt;': '<', '&macr;': '¯', '&mdash;': '—', '&micro;': 'µ', '&minus;': '−', '&Mu;': 'Μ', '&mu;': 'μ', '&nabla;': '∇', '&ndash;': '–', '&ne;': '≠', '&ni;': '∋', '&not;': '¬', '&notin;': '∉', '&nsub;': '⊄', '&Nu;': 'Ν', '&nu;': 'ν', '&OElig;': 'Œ', '&oelig;': 'œ', '&oline;': '‾', '&Omega;': 'Ω', '&omega;': 'ω', '&Omicron;': 'Ο', '&omicron;': 'ο', '&oplus;': '⊕', '&or;': '∨', '&ordf;': 'ª', '&ordm;': 'º', '&otimes;': '⊗', '&para;': '¶', '&part;': '∂', '&permil;': '‰', '&perp;': '⊥', '&Phi;': 'Φ', '&phi;': 'φ', '&Pi;': 'Π', '&pi;': 'π', '&piv;': 'ϖ', '&plusmn;': '±', '&pound;': '£', '&prime;': '′', '&Prime;': '″', '&prod;': '∏', '&prop;': '∝', '&Psi;': 'Ψ', '&psi;': 'ψ', '&radic;': '√', '&raquo;': '»', '&rarr;': '→', '&rceil;': '⌉', '&rdquo;': '”', '&reg;': '®', '&rfloor;': '⌋', '&Rho;': 'Ρ', '&rho;': 'ρ', '&rlm;': '\u200f', '&rsaquo;': '›', '&rsquo;': '’', '&sbquo;': '‚', '&Scaron;': 'Š', '&scaron;': 'š', '&sdot;': '⋅', '&sect;': '§', '&shy;': '\xad', '&Sigma;': 'Σ', '&sigma;': 'σ', '&sigmaf;': 'ς', '&sim;': '∼', '&spades;': '♠', '&sub;': '⊂', '&sube;': '⊆', '&sum;': '∑', '&sup;': '⊃', '&sup1;': '¹', '&sup2;': '²', '&sup3;': '³', '&supe;': '⊇', '&Tau;': 'Τ', '&tau;': 'τ', '&there4;': '∴', '&Theta;': 'Θ', '&theta;': 'θ', '&thetasym;': 'ϑ', '&thinsp;': '\u2009', '&tilde;': '˜', '&times;': '×', '&trade;': '™', '&uarr;': '↑', '&uml;': '¨', '&upsih;': 'ϒ', '&Upsilon;': 'Υ', '&upsilon;': 'υ', '&Xi;': 'Ξ', '&xi;': 'ξ', '&yen;': '¥', '&Yuml;': 'Ÿ', '&Zeta;': 'Ζ', '&zeta;': 'ζ', '&zwj;': '\u200d', '&zwnj;': '\u200c', '&#32;': ' ', '&#33;': '!', '&#34;': '"', '&#35;': '#', '&#36;': '$', '&#37;': '%', '&#38;': '&', '&#39;': "'", '&#40;': '(', '&#41;': ')', '&#42;': '*', '&#43;': '+', '&#44;': ',', '&#45;': '-', '&#46;': '.', '&#47;': '/', '&#48;': '0', '&#49;': '1', '&#50;': '2', '&#51;': '3', '&#52;': '4', '&#53;': '5', '&#54;': '6', '&#55;': '7', '&#56;': '8', '&#57;': '9', '&#58;': ':', '&#59;': ';', '&#60;': '<', '&#61;': '=', '&#62;': '>', '&#63;': '?', '&#64;': '@', '&#65;': 'A', '&#66;': 'B', '&#67;': 'C', '&#68;': 'D', '&#69;': 'E', '&#70;': 'F', '&#71;': 'G', '&#72;': 'H', '&#73;': 'I', '&#74;': 'J', '&#75;': 'K', '&#76;': 'L', '&#77;': 'M', '&#78;': 'N', '&#79;': 'O', '&#80;': 'P', '&#81;': 'Q', '&#82;': 'R', '&#83;': 'S', '&#84;': 'T', '&#85;': 'U', '&#86;': 'V', '&#87;': 'W', '&#88;': 'X', '&#89;': 'Y', '&#90;': 'Z', '&#91;': '[', '&#92;': '\\', '&#93;': ']', '&#94;': '^', '&#95;': '_', '&#96;': '`', '&#97;': 'a', '&#98;': 'b', '&#99;': 'c', '&#100;': 'd', '&#101;': 'e', '&#102;': 'f', '&#103;': 'g', '&#104;': 'h', '&#105;': 'i', '&#106;': 'j', '&#107;': 'k', '&#108;': 'l', '&#109;': 'm', '&#110;': 'n', '&#111;': 'o', '&#112;': 'p', '&#113;': 'q', '&#114;': 'r', '&#115;': 's', '&#116;': 't', '&#117;': 'u', '&#118;': 'v', '&#119;': 'w', '&#120;': 'x', '&#121;': 'y', '&#122;': 'z', '&#123;': '{', '&#124;': '|', '&#125;': '}', '&#126;': '~', '&#160;': ' ', '&#161;': '¡', '&#162;': '¢', '&#163;': '£', '&#164;': '¤', '&#165;': '¥', '&#166;': '¦', '&#167;': '§', '&#168;': '¨', '&#169;': '©', '&#170;': 'ª', '&#171;': '«', '&#172;': '¬', '&#173;': '\xad', '&#174;': '®', '&#175;': '¯', '&#176;': '°', '&#177;': '±', '&#178;': '²', '&#179;': '³', '&#180;': '´', '&#181;': 'µ', '&#182;': '¶', '&#184;': '¸', '&#185;': '¹', '&#186;': 'º', '&#187;': '»', '&#188;': '¼', '&#189;': '½', '&#190;': '¾', '&#191;': '¿', '&#215;': '×', '&#247;': '÷', '&#8704;': '∀', '&#8706;': '∂', '&#8707;': '∃', '&#8709;': '∅', '&#8711;': '∇', '&#8712;': '∈', '&#8713;': '∉', '&#8715;': '∋', '&#8719;': '∏', '&#8721;': '∑', '&#8722;': '−', '&#8727;': '∗', '&#8730;': '√', '&#8733;': '∝', '&#8734;': '∞', '&#8736;': '∠', '&#8743;': '∧', '&#8744;': '∨', '&#8745;': '∩', '&#8746;': '∪', '&#8747;': '∫', '&#8756;': '∴', '&#8764;': '∼', '&#8773;': '≅', '&#8776;': '≈', '&#8800;': '≠', '&#8801;': '≡', '&#8804;': '≤', '&#8805;': '≥', '&#8834;': '⊂', '&#8835;': '⊃', '&#8836;': '⊄', '&#8838;': '⊆', '&#8839;': '⊇', '&#8853;': '⊕', '&#8855;': '⊗', '&#8869;': '⊥', '&#8901;': '⋅', '&#913;': 'Α', '&#914;': 'Β', '&#915;': 'Γ', '&#916;': 'Δ', '&#917;': 'Ε', '&#918;': 'Ζ', '&#919;': 'Η', '&#920;': 'Θ', '&#921;': 'Ι', '&#922;': 'Κ', '&#923;': 'Λ', '&#924;': 'Μ', '&#925;': 'Ν', '&#926;': 'Ξ', '&#927;': 'Ο', '&#928;': 'Π', '&#929;': 'Ρ', '&#931;': 'Σ', '&#932;': 'Τ', '&#933;': 'Υ', '&#934;': 'Φ', '&#935;': 'Χ', '&#936;': 'Ψ', '&#937;': 'Ω', '&#945;': 'α', '&#946;': 'β', '&#947;': 'γ', '&#948;': 'δ', '&#949;': 'ε', '&#950;': 'ζ', '&#951;': 'η', '&#952;': 'θ', '&#953;': 'ι', '&#954;': 'κ', '&#955;': 'λ', '&#956;': 'μ', '&#957;': 'ν', '&#958;': 'ξ', '&#959;': 'ο', '&#960;': 'π', '&#961;': 'ρ', '&#962;': 'ς', '&#963;': 'σ', '&#964;': 'τ', '&#965;': 'υ', '&#966;': 'φ', '&#967;': 'χ', '&#968;': 'ψ', '&#969;': 'ω', '&#977;': 'ϑ', '&#978;': 'ϒ', '&#982;': 'ϖ', '&#338;': 'Œ', '&#339;': 'œ', '&#352;': 'Š', '&#353;': 'š', '&#376;': 'Ÿ', '&#402;': 'ƒ', '&#710;': 'ˆ', '&#732;': '˜', '&#8194;': '\u2002', '&#8195;': '\u2003', '&#8201;': '\u2009', '&#8204;': '\u200c', '&#8205;': '\u200d', '&#8206;': '\u200e', '&#8207;': '\u200f', '&#8211;': '–', '&#8212;': '—', '&#8216;': '‘', '&#8217;': '’', '&#8218;': '‚', '&#8220;': '“', '&#8221;': '”', '&#8222;': '„', '&#8224;': '†', '&#8225;': '‡', '&#8226;': '•', '&#8230;': '…', '&#8240;': '‰', '&#8242;': '′', '&#8243;': '″', '&#8249;': '‹', '&#8250;': '›', '&#8254;': '‾', '&#8364;': '€', '&#8482;': '™', '&#8592;': '←', '&#8593;': '↑', '&#8594;': '→', '&#8595;': '↓', '&#8596;': '↔', '&#8629;': '↵', '&#8968;': '⌈', '&#8969;': '⌉', '&#8970;': '⌊', '&#8971;': '⌋', '&#9674;': '◊', '&#9824;': '♠', '&#9827;': '♣', '&#9829;': '♥', '&#9830;': '♦'}
pattern = r'{}'.format('|'.join(sorted(re.escape(k) for k in html_chars)))
search_re = re.compile(pattern,re.IGNORECASE)
# End Usado na função replaceHtmlChars *****


STOPWORDS_PT = ['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é',
                'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as',
                'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu',
                'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está',
                'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre',
                'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem', 'nas',
                'me', 'esse', 'eles', 'estão', 'você', 'tinha', 'foram', 'essa',
                'num', 'nem', 'suas', 'meu', 'às', 'minha', 'têm', 'numa', 'pelos',
                'elas', 'havia', 'seja', 'qual', 'será', 'nós', 'tenho', 'lhe', 'deles',
                'essas', 'esses', 'pelas', 'este', 'fosse', 'dele', 'tu', 'te', 'vocês',
                'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso',
                'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'estas',
                'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou',
                'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos',
                'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos',
                'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos',
                'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há',
                'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera',
                'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos',
                'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá',
                'houveremos', 'houverão', 'houveria', 'houveríamos', 'houveriam', 'sou',
                'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora',
                'fôramos', 'seja', 'sejamos', 'sejam', 'fosse', 'fôssemos', 'fossem', 'for',
                'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria', 'seríamos',
                'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha', 'tínhamos', 'tinham',
                'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha',
                'tenhamos', 'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver',
                'tivermos', 'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria',
                'teríamos', 'teriam']

STOPWORDS_EN = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
                "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself",
                "she", "her", "hers", "herself", "it", "its", "itself", "they", "them",
                "their", "theirs", "themselves", "what", "which", "who", "whom", "this",
                "that", "these", "those", "am", "is", "are", "was", "were", "be", "been",
                "being", "have", "has", "had", "having", "do", "does", "did", "doing",
                "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
                "while", "of", "at", "by", "for", "with", "about", "against", "between",
                "into", "through", "during", "before", "after", "above", "below", "to",
                "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
                "further", "then", "once", "here", "there", "when", "where", "why", "how",
                "all", "any", "both", "each", "few", "more", "most", "other", "some",
                "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
                "very", "s", "t", "can", "will", "just", "don", "should", "now"]

def capitalizar_nome(nome_completo: str) -> str:
    """
    Capitaliza uma string para o formato Title Case, excluindo 
    palavras de conexão (stop words) como 'do', 'da', 'e', etc.

    Args:
        nome_completo: A string de nome a ser capitalizada (ex: 'universidade federal do parana').

    Returns:
        A string capitalizada corretamente (ex: 'Universidade Federal do Parana').
    """
    

    nome_completo = nome_completo.lower()
    
    palavras = nome_completo.split()
    
    palavras_capitalizadas = []
    
    for i, palavra in enumerate(palavras):
        # Remove caracteres indesejados ou espaços extras antes de verificar
        palavra_limpa = palavra.strip()
        
        # Se a palavra for vazia, continua
        if not palavra_limpa:
            continue
            
        # Condição de Capitalização:
        # 1. Se for a primeira palavra da frase (i == 0), SEMPRE capitaliza.
        # 2. Se a palavra NÃO estiver no conjunto de exceções, capitaliza.
        if i == 0 or palavra_limpa not in PALAVRAS_DE_EXCECAO:
            # Capitaliza a primeira letra e mantém o resto em minúsculo
            palavras_capitalizadas.append(palavra_limpa.capitalize())
        else:
            # Se for uma palavra de exceção E não for a primeira, mantém em minúsculo
            palavras_capitalizadas.append(palavra_limpa)
            
    # Junta as palavras de volta em uma única string
    return " ".join(palavras_capitalizadas)

def replaceHtmlChars(text):
    """Remove os caracteres especiais usados em HTML

    Args:
        text (_type_): Texto a ser tratado

    Returns:
        _type_: Texto sem os caracteres expeciais HTML
    """
    return re.sub(pattern, lambda m: html_chars.get(m.group(0)), text, flags=re.IGNORECASE)

def removeStopwords(text):
    """Remove os stops words

    Args:
        text (_type_): Texto a ser tratado

    Returns:
        _type_: Texto sem StopWords
    """
    return ' '.join([i for i in str(text).replace('\'', ' ').split(' ') if i and i.lower() not in STOPWORDS_PT + STOPWORDS_EN])


def remove_espacos_antes_e_depois(arg):
    if arg is str:
        arg = re.sub(r"^\s+|\s+$", "", arg)
    return arg

def trata_string(txt) -> str:
    if txt is None:
        return None
    stxt = str(txt).strip()
    # return  unidecode(stxt)
    return stxt