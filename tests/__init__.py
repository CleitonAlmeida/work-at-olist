import logging

def set_logger(self, config):
    logger = logging.getLogger()
    fh = logging.handlers.RotatingFileHandler(config.LOG_PATH, maxBytes=int(config.LOG_MAX_BYTES), backupCount=int(config.LOG_BACKUP_COUNT))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
    return logger
