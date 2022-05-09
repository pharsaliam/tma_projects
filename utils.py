import pickle
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


def open_dict_as_pkl(dict_type, directory='episode_dicts'):
    assert dict_type in DICT_TYPES
    with open(f'{directory}/{dict_type}.pkl', 'rb') as f:
        ed = pickle.load(f)
    return ed


def save_dict_as_pkl(episode_dict, dict_type, directory='episode_dicts', logger=None):
    assert dict_type in DICT_TYPES
    location = f'{directory}/{dict_type}.pkl'
    with open(location, 'wb') as outfile:
        pickle.dump(episode_dict, outfile)
    if logger:
        logger.info(f'Saved {dict_type} in {location}')
    return None

def retrieve_included_edges_and_nodes(directory='episode_dicts', minimum_episode_appearances=MIN_EPISODE_APPEARANCES):
    node_appearance_dict = open_dict_as_pkl('na', directory=directory)
    edges_appearance_dict = open_dict_as_pkl('ea', directory=directory)
    nodes_incl = [node for node, node_appearances in node_appearance_dict.items() if len(node_appearances) > minimum_episode_appearances]
    edges_incl = [edge for edge, edge_appearance in edges_appearance_dict.items() if
                  (edge[0] in nodes_incl) & (edge[1] in nodes_incl)]
    return nodes_incl, edges_incl
