import pickle

from utils import load_config

CONFIG = load_config()
DICT_TYPES = CONFIG['DICT_TYPES']
DICT_DIRECTORY = CONFIG['DICT_DIRECTORY']


def open_dict_as_pkl(dict_type, directory=DICT_DIRECTORY):
    """
    Opens a .pkl file to load a TMA dictionary
    :param dict_type: One of four options:
        1. 'individual' for individual episode dict
        2. 'cumulative' for  cumulative episode dict
        3. 'ea' for edge appearance dict
        4. 'na' for node appearance dict
    :type dict_type: str
    :param directory: Directory in which .pkl file is saved
    :type directory: str
    :return: a dict of the specified type
    :rtype: dict
    """
    assert dict_type in DICT_TYPES
    with open(f'{directory}/{dict_type}.pkl', 'rb') as f:
        ed = pickle.load(f)
    return ed


def save_dict_as_pkl(
    episode_dict, dict_type, directory=DICT_DIRECTORY, logger=None
):
    """
    Saves a TMA dictionary as a .pkl file
    :param episode_dict: episode dict to save
    :type episode_dict: dict
    :param dict_type: One of four options:
        1. 'individual' for individual episode dict
        2. 'cumulative' for  cumulative episode dict
        3. 'ea' for edge appearance dict
        4. 'na' for node appearance dict
    :type dict_type: str
    :param directory: Directory in which .pkl file is saved
    :type directory: str
    :return: a dict of the specified type
    :param logger: logging.Logger object
    :type logger: logging.Logger object
    :return: None
    :rtype: None
    """
    assert dict_type in DICT_TYPES
    location = f'{directory}/{dict_type}.pkl'
    with open(location, 'wb') as outfile:
        pickle.dump(episode_dict, outfile)
    if logger:
        logger.info(f'Saved {dict_type} in {location}')
    return None
