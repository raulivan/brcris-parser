import configparser
import sys
import os

# Adiciona o diretório 'src' ao path para permitir importações relativas e não erro de caminhos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))





from util.error_logger import setup_logger

# Importando os validators
from validators.course_validator import CourseValidator
from validators.orcid_validator import OrcidValidator
from validators.person_validator import PersonValidator
from validators.journal_validator import JournalValidator
from validators.orgunit_validator import OrgUnitValidator
from validators.language_validator import LanguageValidator
from validators.publication_capitulo_livro_validator import PublicationCapituloLivroValidator
from validators.publication_doi_validator import PublicationDOIValidator
from validators.publication_eventos_validator import PublicationEventosValidator
from validators.publication_formacao_validator import PublicationFormacaoValidator
from validators.publication_livros_validator import PublicationLivrosValidator
from validators.publication_orcid_validator import PublicationORCIDValidator
from validators.publication_orientacoes_validator import PublicationOrientacoesValidator
from validators.publication_artigo_validator import PublicationArtigoValidator

# Importando os readers
from readers.csv_reader import CSVReader
from readers.json_reader import JSONReader
from readers.jsonl_reader import JSONLReader
from readers.jsonl_gz_reader import JSONLGZReader
from readers.xml_reader import XMLReader
from readers.xml_zip_reader import ZipXMLReader

# Importando os mappersa
from mappers.sucupira_to_program_and_course import Sucupira2ProgramAndCourseMapper
from mappers.revista_open_alex_to_journal import RevistaOpenAlex2JournalMapper
from mappers.publication_open_alex_to_publication import PublicationOpenAlex2PublicationMapper
from mappers.patentes_brcris_to_patent import PatentBrcris2PatentMapper
from mappers.livros_lattes_to_publication import LivroPlataformaLattes2PublicationMapper
from mappers.artigos_lattes_to_publication import ArtigoPlataformaLattes2PublicationMapper
from mappers.capitulo_livros_lattes_to_publication import CapituloLivroPlataformaLattes2PublicationMapper
from mappers.eventos_lattes_to_publication import EventosPlataformaLattes2PublicationMapper
from mappers.orientacao_lattes_to_mestrado_publication import OrientacaoPlataformaLattes2MestradoPublicationMapper
from mappers.orientacao_lattes_to_doutorado_publication import OrientacaoPlataformaLattes2DoutoradoPublicationMapper
from mappers.formacao_lattes_to_publication import FormacaoPlataformaLattes2PublicationMapper
from mappers.publication_oases_to_publication import PublicationOASIS2PublicationMapper
from mappers.relacionamento_grupo_pesquisa import RelacionamentoGrupoPesquisaMapper

# Importando o  writer
from writers.xml_writer import XMLWriter 

# Importando os dictionary builders
from dictionary_builders.journal_dictionary import JournalDictionaryBuilder
from dictionary_builders.orcid_csv_builder import OrcidCSVBuilder
from dictionary_builders.course_dictionary import CourseDictionaryBuilder
from dictionary_builders.publication_dictionary import PublicationDictionaryBuilder

# Mapeia strings de configuração para as classes reais
READER_FACTORY = {
    'csv': CSVReader,
    'json': JSONReader,
    'jsonl': JSONLReader,
    'jsonl.gz': JSONLGZReader,
    'xml': XMLReader,
    'xml.zip': ZipXMLReader,
    
}

WRITER_FACTORY = {
    'xml': XMLWriter, 
}

MAPPER_FACTORY = {
    'sucupira_to_program_and_course_mapper':Sucupira2ProgramAndCourseMapper,
    'revista_open_alex_to_journal_mapper': RevistaOpenAlex2JournalMapper,
    'publication_open_alex_to_publication_mapper': PublicationOpenAlex2PublicationMapper,
    'orientacao_lattes_to_mestrado_publication_mapper': OrientacaoPlataformaLattes2MestradoPublicationMapper,
    'patentes_brcris_to_patent_mapper': PatentBrcris2PatentMapper,
    'livros_lattes_to_publication_mapper': LivroPlataformaLattes2PublicationMapper,
    'artigos_lattes_to_publication_mapper':ArtigoPlataformaLattes2PublicationMapper,
    'capitulo_livro_lattes_to_publication_mapper': CapituloLivroPlataformaLattes2PublicationMapper,
    'evento_lattes_to_publication_mapper': EventosPlataformaLattes2PublicationMapper,
    'orientacao_lattes_to_doutorado_publication_mapper': OrientacaoPlataformaLattes2DoutoradoPublicationMapper,
    'formacao_lattes_to_publication_mapper': FormacaoPlataformaLattes2PublicationMapper,
    'publication_oasis_to_publication_mapper': PublicationOASIS2PublicationMapper,
    'relacionamento_grupo_pesquisa_mapper': RelacionamentoGrupoPesquisaMapper,
}

DICTIONARY_BUILDERS = {
    'Journal':JournalDictionaryBuilder,
    'Course': CourseDictionaryBuilder,
    'Publication': PublicationDictionaryBuilder,
}

logger = setup_logger()

def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """
    Função para capturar qualquer erro não tratado que faria o programa crashar.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Permite que Ctrl+C funcione
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical(
        "Erro Fatal Não Tratado (Uncaught Exception)", 
        exc_info=(exc_type, exc_value, exc_traceback)
    )


def process_transformation(config_section: str):
    
    
    #Carrega conjuntos de dado externos de validação
    orgUnitValidator = OrgUnitValidator()
    orgUnitValidator.load_dataset(r'.\src\data\orgunit2026.json')

    journalValidator = JournalValidator()
    # journalValidator.load_dataset(r'.\src\data\journals2026.json')

    languageValidator = LanguageValidator()
    # languageValidator.load_dataset(r'.\src\data\language2026.json')

    personValidator = PersonValidator()
    personValidator.load_dataset(r'.\src\data\ids_lattes2026.csv')

    orcidValidator = OrcidValidator()
    # orcidValidator.load_dataset(r'.\src\data\orcid_autoridade2026.csv')

    courseValidator= CourseValidator()
    # courseValidator.load_dataset(r'.\src\data\couse_autoridade2026.csv')

    publicationArtigoValidator = PublicationArtigoValidator()
    # publicationArtigoValidator.load_dataset(r'.\src\data\publication_artigo2026.json')

    publicationCapituloLivroValidator = PublicationCapituloLivroValidator()
    # publicationCapituloLivroValidator.load_dataset(r'.\src\data\publication_capitulo_livro2026.json')

    publicationDOIValidator = PublicationDOIValidator()
    # publicationDOIValidator.load_dataset(r'.\src\data\publication_doi2026.json')

    publicationEventosValidator = PublicationEventosValidator()
    # publicationEventosValidator.load_dataset(r'.\src\data\publication_eventos2026.json')

    publicationFormacaoValidator = PublicationFormacaoValidator()
    # publicationFormacaoValidator.load_dataset(r'.\src\data\publication_formacao2026.json')

    publicationLivrosValidator = PublicationLivrosValidator()
    # publicationLivrosValidator.load_dataset(r'.\src\data\publication_livros2026.json')

    publicationORCIDValidator = PublicationORCIDValidator()
    # publicationORCIDValidator.load_dataset(r'.\src\data\publication_orcid2026.json')

    publicationOrientacoesValidator = PublicationOrientacoesValidator()
    # publicationOrientacoesValidator.load_dataset(r'.\src\data\publication_orientacoes2026.json')

    #Carrega o arquivo de configuração da  estrategia de carga dos dados
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Carrega as estratégias de leitura, conversão e escrita dos dados
    reader_type = config.get(config_section, 'reader')
    mapper_type = config.get(config_section, 'mapper')
    writer_type = config.get(config_section, 'writer')

    # Carrega os diretórios de entrada e saída
    input_dir = config.get(config_section, 'input_files')
    output_dir = config.get(config_section, 'output_files')

    # Cria o diretório de saída caso o memso nãoexista pra evitar erros
    os.makedirs(output_dir, exist_ok=True)

    # Instancia as classes uma única vez
    reader = READER_FACTORY.get(reader_type)()
    mapper = MAPPER_FACTORY.get(mapper_type)()
    writer = WRITER_FACTORY.get(writer_type)()

    print(f"Iniciando transformação '{config_section}'...")

    # Define o caminho para o arquivo de checkpoint
    checkpoint_file = os.path.join(output_dir, f"checkpoint_{config_section}.chk")

    # Carrega os arquivos já processados para um "set" (busca muito rápida O(1))
    processed_files = set()
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            processed_files = set(line.strip() for line in f)

    # Itera sobre todos os arquivos no diretório de entrada
    for filename in os.listdir(input_dir):
        try:
            input_path = os.path.join(input_dir, filename)

            # Verifica se ja foi processado
            if filename in processed_files:
                print(f"  {input_path} já processado antriormenter. Pulando...")
                continue

            print(f"  Processando: {input_path}")
            source_data = reader.read(input_path)
            transformed_data = mapper.transform(records=source_data,logger=logger, validators=[orgUnitValidator, 
                                                                                               journalValidator, 
                                                                                               languageValidator, 
                                                                                               personValidator, 
                                                                                               orcidValidator, 
                                                                                               courseValidator,
                                                                                               publicationArtigoValidator,
                                                                                               publicationCapituloLivroValidator,
                                                                                               publicationDOIValidator,
                                                                                               publicationEventosValidator,
                                                                                               publicationFormacaoValidator,
                                                                                               publicationLivrosValidator,
                                                                                               publicationORCIDValidator,
                                                                                               publicationOrientacoesValidator
                                                                                               ])
            writer.write(mapper.get_source(), transformed_data, output_dir)

            # --- SUCESSO: Registrar no checkpoint ---
            with open(checkpoint_file, 'a') as f:
                f.write(f"{filename}\n")
            processed_files.add(filename)

        except KeyboardInterrupt:
            print("\nInterrupção detectada! O progresso foi salvo. Você pode retomar depois.")
        except Exception as e:
            print(f"\nErro ao processar arquivo {filename}: {e}")

    print(f"Transformação '{config_section}' concluída. Arquivos salvos em '{output_dir}'.")
    

def dictionary_builder(entity, source_path, output_path):
    builder = DICTIONARY_BUILDERS.get(entity)()
    builder.process_xml_files(source_path, output_path)
    
if __name__ == "__main__":
    sys.excepthook = handle_uncaught_exception

    process_transformation('RELACIONAMENTO_GRUPO_PESQUISA')
    # dictionary_builder(entity='Publication',output_path='.\src\data\output',source_path=r"C:\IBICT-DATA\2025\PublicationORCID")
    # OrcidCSVBuilder().make_csv_dataset(r'.\src\data\cabecalho_2024_20250110.csv')

