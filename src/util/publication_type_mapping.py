class BrCrisTypes:
    ARTIGO = "Artigo"
    CONFERENCIA = "Artigo de Conferência"
    TESE = "Tese"
    DISSERTACAO = "Dissertação"
    LIVRO = "Livro"
    CAPITULO = "Capítulo de Livro"
    DATASET = "Conjunto de Dados"
    PREPRINT = "Preprint"
    OUTRO = None

class PublicationTypeMapping:
    # Mapeamento Lattes -> BrCris
    LATTES_MAP = {
        "artigos completos publicados em periódicos": BrCrisTypes.ARTIGO,
        "trabalhos completos publicados em anais de congressos": BrCrisTypes.CONFERENCIA,
        "resumos expandidos publicados em anais de congressos": BrCrisTypes.CONFERENCIA,
        "resumos publicados em anais de congressos": BrCrisTypes.CONFERENCIA,
        "livros publicados/organizados ou edições": BrCrisTypes.LIVRO,
        "capítulos de livros publicados": BrCrisTypes.CAPITULO,
        "dissertação de mestrado": BrCrisTypes.DISSERTACAO,
        "tese de doutorado": BrCrisTypes.TESE,
        "MONOGRAFIA_DE_CONCLUSAO_DE_CURSO_APERFEICOAMENTO_E_ESPECIALIZACAO": BrCrisTypes.OUTRO,
        "TRABALHO_DE_CONCLUSAO_DE_CURSO_GRADUACAO": BrCrisTypes.OUTRO,
        "ORIENTACAO-DE-OUTRA-NATUREZA": BrCrisTypes.OUTRO,
    }


    # Mapeamento OpenAlex -> BrCris
    OPENALEX_MAP = {
        "article": BrCrisTypes.ARTIGO,
        "review article": BrCrisTypes.ARTIGO,
        "original research": BrCrisTypes.PREPRINT,
        "preprint": BrCrisTypes.PREPRINT,
        "conference paper": BrCrisTypes.CONFERENCIA,
        "proceedings": BrCrisTypes.CONFERENCIA,
        "dissertation": BrCrisTypes.DISSERTACAO,
        "thesis": BrCrisTypes.TESE,
        "book-chapter": BrCrisTypes.CAPITULO,
        "book": BrCrisTypes.LIVRO,
        "dataset": BrCrisTypes.DATASET
    }

    @classmethod
    def get_brcris_type(cls, source_type: str, source_name: str) -> str:
        if not source_type:
            return BrCrisTypes.OUTRO

        source_name = source_name.upper()
        
        if source_name == "LATTES":
            return cls.LATTES_MAP.get(source_type.lower(), BrCrisTypes.OUTRO)
        
        if source_name == "OPENALEX":
            return cls.OPENALEX_MAP.get(source_type.lower(), BrCrisTypes.OUTRO)
        
        return BrCrisTypes.OUTRO