import configparser
import sys
import os





# Adiciona o diretório 'src' ao path para permitir importações relativas e não erro de caminhos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importando os validators
from validators.journal_validator import JournalValidator
from validators.orgunit_validator import OrgUnitValidator
from validators.language_validator import LanguageValidator


# Importando os readers
from readers.csv_reader import CSVReader
from readers.json_reader import JSONReader
from readers.jsonl_reader import JSONLReader
from readers.jsonl_gz_reader import JSONLGZReader

# Importando os mappersa
from mappers.sucupira_to_program_and_course import Sucupira2ProgramAndCourseMapper
from mappers.revista_open_alex_to_journal import RevistaOpenAlex2JournalMapper
from mappers.publication_open_alex_to_publication import PublicationOpenAlex2PublicationMapper
from mappers.orientacao_lattes_to_publication import OrientacaoPlataformaLattes2PublicationMapper


# Importando o novo writer
from writers.xml_writer import XMLWriter # Importa o novo writer

# Importando os dictionary builders
from dictionary_builders.journal_dictionary import JournalDictionaryBuilder

# Mapeia strings de configuração para as classes reais
READER_FACTORY = {
    'csv': CSVReader,
    'json': JSONReader,
    'jsonl': JSONLReader,
    'jsonl.gz': JSONLGZReader,
    
}

WRITER_FACTORY = {
    'xml': XMLWriter, 
}

MAPPER_FACTORY = {
    'sucupira_to_program_and_course_mapper':Sucupira2ProgramAndCourseMapper,
    'revista_open_alex_to_journal_mapper': RevistaOpenAlex2JournalMapper,
    'publication_open_alex_to_publication_mapper': PublicationOpenAlex2PublicationMapper,
    'orientacao_lattes_to_publication_mapper': OrientacaoPlataformaLattes2PublicationMapper
}

DICTIONARY_BUILDERS = {
    'Journal':JournalDictionaryBuilder,
}


def process_transformation(config_section: str):
    #Carrega conjuntos de dado externos de validação
    orgUnitValidator = OrgUnitValidator()
    orgUnitValidator.load_dataset(r'.\src\data\orgunit.json')

    journalValidator = JournalValidator()
    journalValidator.load_dataset(r'.\src\data\journals.json')

    languageValidator = LanguageValidator()
    languageValidator.load_dataset(r'.\src\data\language.json')

    
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
            transformed_data = mapper.transform(records=source_data,validators=[orgUnitValidator, journalValidator, languageValidator])
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
    process_transformation('PUBLICACOES_OPEN_ALEX_DOI')
    # process_transformation('ORIENTACOES_PLATAFORMA_LATTES')
    # dictionary_builder(entity='Journal',output_path='.\src\data\output',source_path=r"C:\IBICT-DATA\2025\Journal")
