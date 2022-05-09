import logging

DICT_TYPES = ['individual', 'cumulative', 'ea', 'na']
MIN_EPISODE_APPEARANCES = 2


def create_logger(logger_name, logging_level='INFO'):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p'
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger
