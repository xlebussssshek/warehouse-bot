import logging
from config import LOG_FILE

def setup_logger():
    logger = logging.getLogger('warehouse_bot')
    logger.setLevel(logging.INFO)

    # Формат: 2026-02-11 14:35:22 | user 123456789 | /add A-001 5 | успех
    formatter = logging.Formatter(
        "%(asctime)s | user %(user_id)s | %(command)s | %(text)s",
        datefmt="%Y-%m-%d %H-%M-%S"
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

logger = setup_logger()