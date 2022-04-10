import copy
import argparse
import pickle

from utils import create_logger
from tma_episode_processor import TMAEpisode

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
    default='episode_dicts'
)
args = parser.parse_args()
if args.end_episode < args.start_episode:
    parser.error('Start episode # must be less than end episode #')
logger = create_logger('episode_dicts', logging_level=args.logging_level.upper())


def generate_individual_episode_dict(start_episode, end_episode):
    list_of_episodes = [i for i in range(start_episode, end_episode+1)]
    logger.debug(f'{list_of_episodes=}')
    individual_episode_dict = {}
    for e in list_of_episodes:
        episode = TMAEpisode(e, logging_level=args.logging_level)
        logger.info(f'Episode {e} created')
        episode()
        individual_episode_dict[e] = {
            'nodes': episode.nodes,
            'edge_dict': episode.edges_dict
        }
    return individual_episode_dict


def generate_cumulative_episode_dict(individual_episode_dict):
    cumulative_episode_dict = {}
    for e in individual_episode_dict:
        prev_e = e - 1
        if prev_e in cumulative_episode_dict:
            prev_nodes = copy.deepcopy(cumulative_episode_dict[prev_e]['nodes'])
            prev_edge_dict = copy.deepcopy(cumulative_episode_dict[prev_e]['edge_dict'])
            current_nodes = copy.deepcopy(individual_episode_dict[e]['nodes'])
            current_edge_dict = copy.deepcopy(individual_episode_dict[e]['edge_dict'])
            for edge, edge_attributes in current_edge_dict.items():
                if edge in prev_edge_dict:
                    prev_edge_dict[edge]['weight'] += edge_attributes[
                        'weight']
                else:
                    prev_edge_dict[edge] = edge_attributes
            cumulative_episode_dict[e] = {
                'nodes': prev_nodes.union(current_nodes),
                'edge_dict': prev_edge_dict
            }
        else:
            cumulative_episode_dict[e] = copy.deepcopy(individual_episode_dict[e])
    return cumulative_episode_dict


def save_dict_as_pkl(episode_dict, dict_type, directory):
    assert dict_type in ('individual', 'cumulative')
    with open(f'{directory}/{dict_type}.pkl', 'wb') as outfile:
        pickle.dump(episode_dict, outfile)
    return None


if __name__ == '__main__':
    logger.info(vars(args))
    indi = generate_individual_episode_dict(args.start_episode, args.end_episode)
    logger.debug(f'Ending episode (i): {indi[args.end_episode]}')
    cumu = generate_cumulative_episode_dict(indi)
    logger.debug(f'Ending episode (c): {cumu[args.end_episode]}')
    save_dict_as_pkl(indi, 'individual', args.save_dir)
    logger.info(f'Saved individual episode dict')
    save_dict_as_pkl(cumu, 'cumulative', args.save_dir)
    logger.info(f'Saved cumulative episode dict')
