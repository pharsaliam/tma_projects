import copy
import argparse
import sys
import os

p = os.path.abspath('.')
sys.path.insert(1, p)

from utils import create_logger, save_dict_as_pkl
from B_episode_dicts.tma_episode_processor import TMAEpisode


def generate_individual_episode_dict(start_episode, end_episode, logger_object=None):
    list_of_episodes = [i for i in range(start_episode, end_episode+1)]
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
            'edges_dict': episode.edges_dict
        }
        update_item_appearance_dict(
            episode.edges_dict,
            edge_appearance_dict,
            episode.number
        )
        update_item_appearance_dict(
            episode.nodes_dict,
            node_appearance_dict,
            episode.number
        )
    return individual_episode_dict, edge_appearance_dict, node_appearance_dict


def update_item_appearance_dict(items_dict, item_appearance_dict, episode_number):
    for item, item_attributes in items_dict.items():
        if item in item_appearance_dict:
            item_appearance_dict[item][episode_number] = item_attributes
        else:
            item_appearance_dict[item] = {episode_number: item_attributes}


def generate_cumulative_episode_dict(individual_episode_dict, logger_object=None):
    cumulative_episode_dict = {}
    for e in individual_episode_dict:
        prev_e = e - 1
        if prev_e in cumulative_episode_dict:
            prev_nodes_dict_update = update_cumulative_items_dict(
                'node',
                cumulative_episode_dict[prev_e],
                individual_episode_dict[e]
            )
            prev_edges_dict_update = update_cumulative_items_dict(
                'edge',
                cumulative_episode_dict[prev_e],
                individual_episode_dict[e]
            )
            cumulative_episode_dict[e] = {
                'nodes_dict': prev_nodes_dict_update,
                'edges_dict': prev_edges_dict_update
            }
        else:
            cumulative_episode_dict[e] = copy.deepcopy(individual_episode_dict[e])
        if logger_object:
            logger_object.info(f'Generated cumulative episode dict for episode {e}')
            logger_object.debug(f'{cumulative_episode_dict}')
    return cumulative_episode_dict


def update_cumulative_items_dict(item_type, previous_episode_dict, current_episode_dict):
    assert item_type in ('node', 'edge')
    item_dict_key = f'{item_type}s_dict'
    attribute = 'size' if item_type == 'node' else 'weight'
    prev_items_dict_update = copy.deepcopy(previous_episode_dict[item_dict_key])
    current_items_dict = copy.deepcopy(current_episode_dict[item_dict_key])
    for item, item_attributes in current_items_dict.items():
        if item in prev_items_dict_update:
            prev_items_dict_update[item][attribute] += item_attributes[attribute]
        else:
            prev_items_dict_update[item] = item_attributes
    return prev_items_dict_update


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--start_episode', '-S',
        type=int,
        default=1,
        choices=range(1, 161),
        help='First episode to include in the dict'
    )
    parser.add_argument(
        '--end_episode', '-E',
        type=int,
        default=160,
        choices=range(1, 161),
        help='Last episode to include in the dict'
    )
    parser.add_argument(
        '--logging_level', '-L',
        type=str.upper,
        default='info',
        help='Python logging level'
    )
    parser.add_argument(
        '--save_dir', '-D',
        type=str,
        default='B_episode_dicts/dicts',
        help='Directory to which to save the episode dicts'
    )
    args = parser.parse_args()
    if args.end_episode < args.start_episode:
        parser.error('Start episode # must be less than end episode #')
    logger = create_logger('episode_dicts',
                           logging_level=args.logging_level.upper())
    logger.info(vars(args))
    indi, ea, na = generate_individual_episode_dict(args.start_episode, args.end_episode, logger)
    logger.info('Finished generating individual episode dict, node appearance dict, and edge appearance dict')
    logger.debug(f'Ending episode (i): {indi[args.end_episode]}')
    cumu = generate_cumulative_episode_dict(indi, logger)
    logger.info('Finished generating cumulative episode dict')
    logger.debug(f'Ending episode (c): {cumu[args.end_episode]}')
    save_dict_as_pkl(na, 'na', args.save_dir, logger)
    save_dict_as_pkl(ea, 'ea', args.save_dir, logger)
    save_dict_as_pkl(indi, 'individual', args.save_dir, logger)
    save_dict_as_pkl(cumu, 'cumulative', args.save_dir, logger)
