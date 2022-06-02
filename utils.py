import pickle
import logging

DICT_TYPES = ['individual', 'cumulative', 'ea', 'na']
MIN_EPISODE_APPEARANCES = 3


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
            datefmt='%m/%d/%Y %I:%M:%S %p'
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


def open_dict_as_pkl(dict_type, directory='B_episode_dicts/dicts'):
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


def save_dict_as_pkl(episode_dict, dict_type, directory='B_episode_dicts/dicts', logger=None):
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


def retrieve_included_edges_and_nodes(directory='B_episode_dicts/dicts', minimum_episode_appearances=MIN_EPISODE_APPEARANCES):
    """
    Retrieve a list of nodes that have hit a minimum episode appearance number
    and the edges relevant to that list of nodes
    :param directory: Directory in which node or edge appearance dict is saved as a .pkl file
    :type directory: str
    :param minimum_episode_appearances: Minimum number of episodes node must appear in to be included
    :type minimum_episode_appearances: int
    :return: list of included nodes, list of included edges
    :rtype: list, list
    """
    node_appearance_dict = open_dict_as_pkl('na', directory=directory)
    edges_appearance_dict = open_dict_as_pkl('ea', directory=directory)
    nodes_incl = [node for node, node_appearances in node_appearance_dict.items() if len(node_appearances) >= minimum_episode_appearances]
    edges_incl = [edge for edge, edge_appearance in edges_appearance_dict.items() if
                  (edge[0] in nodes_incl) & (edge[1] in nodes_incl)]
    return nodes_incl, edges_incl
