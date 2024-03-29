import logging
import os
from datetime import datetime


def configure_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if os.getenv('AWS_EXECUTION_ENV'):
        # We are running on AWS Lambda. Log to stdout.
        handler = logging.StreamHandler()

    else:
        # We are running locally. Log to a file.
        LOG_FILE = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log"
        logs_path = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_path, exist_ok=True)
        LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)
        handler = logging.FileHandler(LOG_FILE_PATH)

    formatter = logging.Formatter('[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
