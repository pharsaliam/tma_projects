import logging
import yaml

MIN_EPISODE_APPEARANCES = 3


def load_config(filename='config.yaml'):
    with open(filename, "r") as file:
        cfg = yaml.safe_load(file)
    return cfg


def create_logger(logger_name, logging_level='INFO'):
    """
    Creates a logging.Logger object and adds a StreamHandler if one is not
    already present
    :param logger_name: Name of logger
    :type logger_name: str
    :param logging_level: A standard Python logging level
            (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    :type logging_level: str
    :return: logging.Logger object
    :rtype: logging.Logger object
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger
