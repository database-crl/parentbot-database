import logging
from datetime import datetime
import os

# Папка для логов
LOG_FOLDER = "logs"

# Создание папки логов, если нет
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

# Файл для логирования
LOG_FILE = os.path.join(LOG_FOLDER, f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def log_info(message: str):
    logging.info(message)

def log_warning(message: str):
    logging.warning(message)

def log_error(message: str):
    logging.error(message)

def log_critical(message: str):
    logging.critical(message)
