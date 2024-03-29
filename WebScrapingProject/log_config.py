import logging
import os
from datetime import datetime


def configure_logger(name):
    LOG_FILE = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log"
    logs_path = os.path.join(os.getcwd(), "logs")
    os.makedirs(logs_path, exist_ok=True)

    LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(LOG_FILE_PATH)
    formatter = logging.Formatter('[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
