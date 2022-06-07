import copy
import argparse
import sys
import os

p = os.path.abspath('.')
sys.path.insert(1, p)

from utils import create_logger, load_config
from B_episode_dicts.tma_episode_processor import TMAEpisode
from B_episode_dicts.save_and_load_dict import save_dict_as_pkl

CONFIG = load_config()
MAX_EPISODE = CONFIG['MAX_EPISODE']
DICT_DIRECTORY = CONFIG['DICT_DIRECTORY']


def generate_individual_episode_dict(
    start_episode, end_episode, logger_object=None
):
    """
    Generates
        1. a nested dictionary where key is an episode number and values
        contain nodes and edges dictionary for the character appearances and
        interactions in the individual episode
        2. a nested dictionary where the key is a character name (node) and
        values contain episode appearance information (words spoken)
        3. a nested dictionary where the key is a character pair (edge) and
        values contain episode appearance information (closeness)
    :param start_episode: First episode to appear in dictionary
    :type start_episode: int
    :param end_episode: Last episode to appear in dictionary
    :type end_episode: int
    :param logger_object: a logging.Logger object
    :type logger_object: logging.Logger object
    :return: Individual episode dictionary, node appearance dict, edge
        appearance dict
    :rtype: dict, dict, dict
    """
    list_of_episodes = [i for i in range(start_episode, end_episode + 1)]
    if logger_object:
        logger_object.debug(f'{list_of_episodes=}')
    individual_episode_dict = {}
    edge_appearance_dict = {}
    node_appearance_dict = {}
    for e in list_of_episodes:
        episode = TMAEpisode(e)
        if logger_object:
            logger_object.info(f'Episode {e} created')
        episode()
        individual_episode_dict[e] = {
            'nodes_dict': episode.nodes_dict,
            'edges_dict': episode.edges_dict,
        }
        update_item_appearance_dict(
            episode.edges_dict, edge_appearance_dict, episode.number
        )
        update_item_appearance_dict(
            episode.nodes_dict, node_appearance_dict, episode.number
        )
    return individual_episode_dict, edge_appearance_dict, node_appearance_dict


def update_item_appearance_dict(
    items_dict, item_appearance_dict, episode_number
):
    """
    Checks for a key in a node/edge appearance dictionary. Adds it with current
    episode appearance attributes if it's not there. Adds to appearance dict
    if it does appear
    :param items_dict: Nodes or edges dict attribute from TMAEpisode
    :type items_dict: dict
    :param item_appearance_dict: Nodes or edges appearance dict where key is
        a node or edge and the values contain information for each episode
        where the node or edge appear and their appearance attributes
    :type item_appearance_dict: dict
    :param episode_number: Current episode number
    :type episode_number: int
    :return: None
    :rtype: None
    """
    for item, item_attributes in items_dict.items():
        if item in item_appearance_dict:
            item_appearance_dict[item][episode_number] = item_attributes
        else:
            item_appearance_dict[item] = {episode_number: item_attributes}
    return None


def generate_cumulative_episode_dict(
    individual_episode_dict, logger_object=None
):
    """
    Generates a nested dictionary where key is an episode number and values
    contain nodes and edges dictionary for the cumulative character
    appearances and interactions up to that episode
    :param individual_episode_dict: a nested dictionary where key is an episode
        number and values contain nodes and edges dictionary for the character
        appearances and interactions in the individual episode
    :type individual_episode_dict: dict
    :param logger_object: a logging.Logger object
    :type logger_object: logging.Logger object
    :return: Cumulative episode dict
    :rtype: dict
    """
    cumulative_episode_dict = {}
    for e in individual_episode_dict:
        prev_e = e - 1
        if prev_e in cumulative_episode_dict:
            prev_nodes_dict_update = update_cumulative_items_dict(
                'node',
                cumulative_episode_dict[prev_e],
                individual_episode_dict[e],
            )
            prev_edges_dict_update = update_cumulative_items_dict(
                'edge',
                cumulative_episode_dict[prev_e],
                individual_episode_dict[e],
            )
            cumulative_episode_dict[e] = {
                'nodes_dict': prev_nodes_dict_update,
                'edges_dict': prev_edges_dict_update,
            }
        else:
            cumulative_episode_dict[e] = copy.deepcopy(
                individual_episode_dict[e]
            )
        if logger_object:
            logger_object.info(
                f'Generated cumulative episode dict for episode {e}'
            )
            logger_object.debug(f'{cumulative_episode_dict}')
    return cumulative_episode_dict


def update_cumulative_items_dict(
    item_type, previous_episode_dict, current_episode_dict
):
    """
    checks if a node/edge has appeared in the previous episode of a cumulative
    episode dict. If it has not, adds it with the current node/edge
    attributes. If it has, adds attribute to the previous episode's attributes
    to generate cumulative attribute for current episode
    if it does appear
    :param item_type: 'node' or 'edge'
    :type item_type: st
    :param previous_episode_dict: cumulative episode dict entry for previous
        episode
    :type previous_episode_dict: dict
    :param current_episode_dict: individual episode dict entry for current
        episode
    :type current_episode_dict: dict
    :return: Updated cumulative episode dict entry for current episode
    :rtype: dict
    """
    assert item_type in ('node', 'edge')
    item_dict_key = f'{item_type}s_dict'
    attribute = 'size' if item_type == 'node' else 'weight'
    prev_items_dict_update = copy.deepcopy(previous_episode_dict[item_dict_key])
    current_items_dict = copy.deepcopy(current_episode_dict[item_dict_key])
    for item, item_attributes in current_items_dict.items():
        if item in prev_items_dict_update:
            prev_items_dict_update[item][attribute] += item_attributes[
                attribute
            ]
        else:
            prev_items_dict_update[item] = item_attributes
    return prev_items_dict_update


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--start_episode',
        '-S',
        type=int,
        default=1,
        choices=range(1, MAX_EPISODE + 1),
        help='First episode to include in the dict',
    )
    parser.add_argument(
        '--end_episode',
        '-E',
        type=int,
        default=MAX_EPISODE,
        choices=range(1, MAX_EPISODE + 1),
        help='Last episode to include in the dict',
    )
    parser.add_argument(
        '--logging_level',
        '-L',
        type=str.upper,
        default='info',
        help='Python logging level',
    )
    parser.add_argument(
        '--save_dir',
        '-D',
        type=str,
        default=DICT_DIRECTORY,
        help='Directory to which to save the episode dicts',
    )
    args = parser.parse_args()
    if args.end_episode < args.start_episode:
        parser.error('Start episode # must be less than end episode #')
    logger = create_logger(
        'episode_dicts', logging_level=args.logging_level.upper()
    )
    logger.info(vars(args))
    indi, ea, na = generate_individual_episode_dict(
        args.start_episode, args.end_episode, logger
    )
    logger.info(
        'Finished generating individual episode dict, node appearance dict, and edge appearance dict'
    )
    logger.debug(f'Ending episode (i): {indi[args.end_episode]}')
    cumu = generate_cumulative_episode_dict(indi, logger)
    logger.info('Finished generating cumulative episode dict')
    logger.debug(f'Ending episode (c): {cumu[args.end_episode]}')
    save_dict_as_pkl(na, 'na', args.save_dir, logger)
    save_dict_as_pkl(ea, 'ea', args.save_dir, logger)
    save_dict_as_pkl(indi, 'individual', args.save_dir, logger)
    save_dict_as_pkl(cumu, 'cumulative', args.save_dir, logger)
