import logging

APP_LOGGER_NAME = 'Main'


def get_logger(module_name):
    return logging.getLogger(APP_LOGGER_NAME).getChild(module_name)


def setup_applevel_logger(logger_name=APP_LOGGER_NAME, file_name=None):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(asctime)s] - %(levelname)s - %(name)s - %(message)s", '%d %H:%M:%S')
    console_out_handler = logging.StreamHandler()
    console_out_handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(console_out_handler)
    if file_name:
        fh = logging.FileHandler(file_name)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger