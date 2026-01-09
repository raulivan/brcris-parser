# BRCris Parser 1.0

Este projeto é uma ferramenta de ETL (Extração, Transformação e Carga) para converter conjuntos de dados para entidades do modelo BrCris.

## Estrutura

O projeto é dividido em três componentes principais:

- **Readers**: Módulos para ler dados de diferentes fontes (CSV, JSON, etc.).
- **Mappers**: Módulos que contêm a lógica de negócio para transformar os dados de um formato de origem para um de destino.
- **Writers**: Módulos para escrever os dados transformados em diferentes formatos.

O fluxo de transformação é orquestrado pelo `src/main.py` e configurado através do arquivo `config.ini`.

## Como Executar

1.  **Instale as dependências:**

    ```bash
    python -m venv venv
    
    .\venv\Scripts\Activate

    pip install -r requirements.txt
    ```

2.  **Coloque os arquivos de entrada** na pasta `data/input/`.

3.  **Execute o script principal:**

    ```bash
    python src/main.py
    ```