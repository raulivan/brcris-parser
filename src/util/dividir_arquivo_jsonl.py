import os

def split_jsonl(input_file, chunk_size_mb=500, output_prefix='output_part_'):
    """
    Quebra um JSONL grande em partes menores baseadas no tamanho em MB,
    preservando a integridade das linhas.
    """
    # Converte MB para Bytes
    max_size_bytes = chunk_size_mb * 1024 * 1024
    
    file_count = 1
    current_size = 0

    out_file = open(f"{output_prefix}{file_count}.jsonl", 'w', encoding='utf-8')
    
    print(f"Iniciando a quebra de {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Calcula o tamanho da linha em bytes
                line_size = len(line.encode('utf-8'))
                
                # Se adicionar essa linha ultrapassar o limite, fecha e abre um novo
                if current_size + line_size > max_size_bytes:
                    out_file.close()
                    print(f"Arquivo {output_prefix}{file_count}.jsonl finalizado ({current_size/1024/1024:.2f} MB).")
                    
                    file_count += 1
                    out_file = open(f"{output_prefix}{file_count}.jsonl", 'w', encoding='utf-8')
                    current_size = 0
                
                out_file.write(line)
                current_size += line_size
                
    except FileNotFoundError:
        print("Arquivo de entrada não encontrado.")
    finally:
        out_file.close()
        print(f"Processo concluído. Total de {file_count} arquivos gerados.")

# --- Configuração ---
ARQUIVO_ORIGEM = r'C:\IBICT-DATA\BRUTOS\lattes\formacao\formacoes.jsonl'
TAMANHO_POR_ARQUIVO_MB = 400  # 400MB


if __name__ == "__main__":

    if os.path.exists(ARQUIVO_ORIGEM):
        split_jsonl(ARQUIVO_ORIGEM, TAMANHO_POR_ARQUIVO_MB)
    else:
        print(f"Por favor, aponte para o seu arquivo real em 'ARQUIVO_ORIGEM'")