import logging
import os
from datetime import datetime


class CustomLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET, logs_handler=None):
        super().__init__(name, level)
        self.logs_handler = logs_handler

    def get_logs(self):
        if self.logs_handler:
            return self.logs_handler.get_logs()
        return []


class InfoListHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs = []

    def emit(self, record):
        if record.levelno == logging.INFO:
            self.logs.append(self.format(record))

    def get_logs(self):
        return self.logs


def configure_logger(name):
    logger = CustomLogger(name)
    logger.setLevel(logging.DEBUG)

    if os.getenv('AWS_EXECUTION_ENV'):
        handler = logging.StreamHandler()
    else:
        LOG_FILE = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log"
        logs_path = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_path, exist_ok=True)
        LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)
        handler = logging.FileHandler(LOG_FILE_PATH)

    formatter = logging.Formatter('[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    info_list_handler = InfoListHandler()
    info_list_handler.setFormatter(formatter)
    logger.addHandler(info_list_handler)
    logger.logs_handler = info_list_handler  # add the new handler to allow accessing its 'get_logs' method

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger  # return just the logger
