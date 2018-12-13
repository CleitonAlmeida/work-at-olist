import logging
import os
from call_records.config import app_config

def set_logger(self):
    config = app_config[os.environ['FLASK_ENV']]

    logger = logging.getLogger()
    fh = logging.handlers.RotatingFileHandler(config.LOG_PATH, maxBytes=int(config.LOG_MAX_BYTES), backupCount=int(config.LOG_BACKUP_COUNT))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
    return logger
