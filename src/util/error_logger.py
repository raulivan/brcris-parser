import logging
import sys
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler
import os

class JsonFormatter(logging.Formatter):
    """
    Formata o log como um objeto JSON para facilitar a ingestão por sistemas de monitoramento.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "line": record.lineno
        }
        
        # Se houver uma exceção/erro, adiciona o Stack Trace
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

# def setup_logger():
#     logger = logging.getLogger("BrCrisParser")
#     logger.setLevel(logging.INFO)

#     # Handler para enviar logs para o console (stdout)
#     handler = logging.StreamHandler(sys.stdout)
#     handler.setFormatter(JsonFormatter())
    
#     # Evita adicionar handlers duplicados se a função for chamada várias vezes
#     if not logger.handlers:
#         logger.addHandler(handler)
        
#     return logger

def setup_logger():
    logger = logging.getLogger("BrCrisParser")
    logger.setLevel(logging.INFO)

    # Evita duplicar handlers se a função for chamada novamente
    if logger.handlers:
        return logger

    formatter = JsonFormatter()

    # para o CONSOLE (para você ver enquanto programa)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    #  para ARQUIVO (com Rotação)
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Cria o arquivo 'app.log'. Quando chegar em 5MB, ele renomeia para app.log.1
    # Mantém no máximo 3 arquivos de backup.
    file_handler = RotatingFileHandler(
        filename='logs/app.log', 
        maxBytes=5 * 1024 * 1024, # 5 Megabytes
        backupCount=10,            # Mantém 10 arquivos antigos
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
        
    return logger