import logging

logger = logging.getLogger('root')


long_f = "%(levelname)s:%(filename)s:%(funcName)s():%(lineno)s: %(message)s"
short_f = '%(message)s'


def setup_logger(level="INFO", name="root"):
    logger = logging.getLogger(name)
    if len(logger.handlers) == 0:
        logger_handler = logging.StreamHandler()
        logger.addHandler(logger_handler)
    set_logger_level(logger, level)
    return logger

def set_logger_level(logger, level):
    if level == "INFO" or level == logging.INFO:
        logger.handlers[0].setFormatter(logging.Formatter(short_f))
        logger.setLevel(logging.INFO)
    elif level == "DEBUG" or level == logging.DEBUG:
        logger.handlers[0].setFormatter(logging.Formatter(long_f))
        logger.setLevel(logging.DEBUG)
    elif level == "WARNING" or level == logging.WARNING:
        logger.handlers[0].setFormatter(logging.Formatter(long_f))
        logger.setLevel(logging.WARNING)
    else:
        raise AssertionError("Not recognized logger level: {}".format(level))
