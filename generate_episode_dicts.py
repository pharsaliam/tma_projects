import copy
import argparse

from utils import create_logger
from tma_episode_processor import TMAEpisode
from utils import save_dict_as_pkl

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
    edge_appearance_dict = {}
    node_appearance_dict = {}
    for e in list_of_episodes:
        episode = TMAEpisode(e, logging_level=args.logging_level)
        logger.info(f'Episode {e} created')
        episode()
        individual_episode_dict[e] = {
            'nodes_dict': episode.nodes_dict,
            'edges_dict': episode.edges_dict
        }
        # TODO Consolidate this into a function
        for edge, edge_attributes in episode.edges_dict.items():
            if edge in edge_appearance_dict:
                edge_appearance_dict[edge][episode.number] = edge_attributes
            else:
                edge_appearance_dict[edge] = {episode.number: edge_attributes}
        for node, node_attributes in episode.nodes_dict.items():
            if node in node_appearance_dict:
                node_appearance_dict[node][episode.number] = node_attributes
            else:
                node_appearance_dict[node] = {episode.number: node_attributes}
    return individual_episode_dict, edge_appearance_dict, node_appearance_dict


def generate_cumulative_episode_dict(individual_episode_dict):
    cumulative_episode_dict = {}
    for e in individual_episode_dict:
        prev_e = e - 1
        if prev_e in cumulative_episode_dict:
            # Update nodes
            prev_nodes_dict_update = copy.deepcopy(cumulative_episode_dict[prev_e]['nodes_dict'])
            current_nodes_dict = copy.deepcopy(individual_episode_dict[e]['nodes_dict'])
            for node, node_attributes in current_nodes_dict.items():
                # TODO Consolidate this into a function
                if node in prev_nodes_dict_update:
                    prev_nodes_dict_update[node]['size'] += node_attributes['size']
                else:
                    prev_nodes_dict_update[node] = node_attributes
            # Update edges
            prev_edges_dict_update = copy.deepcopy(cumulative_episode_dict[prev_e]['edges_dict'])
            current_edges_dict = copy.deepcopy(individual_episode_dict[e]['edges_dict'])
            for edge, edge_attributes in current_edges_dict.items():
                # TODO Consolidate this into a function
                if edge in prev_edges_dict_update:
                    prev_edges_dict_update[edge]['weight'] += edge_attributes[
                        'weight']
                else:
                    prev_edges_dict_update[edge] = edge_attributes
            # Put it all together
            cumulative_episode_dict[e] = {
                'nodes_dict': prev_nodes_dict_update,
                'edges_dict': prev_edges_dict_update
            }
        else:
            cumulative_episode_dict[e] = copy.deepcopy(individual_episode_dict[e])
        logger.info(f'Generated cumulative episode dict for episode {e}')
        logger.debug(f'{cumulative_episode_dict}')
    return cumulative_episode_dict


if __name__ == '__main__':
    logger.info(vars(args))
    indi, ea, na = generate_individual_episode_dict(args.start_episode, args.end_episode)
    logger.info('Finished generating individual episode dict, node appearance dict, and edge appearance dict')
    logger.debug(f'Ending episode (i): {indi[args.end_episode]}')
    cumu = generate_cumulative_episode_dict(indi)
    logger.info('Finished generating cumulative episode dict')
    logger.debug(f'Ending episode (c): {cumu[args.end_episode]}')
    save_dict_as_pkl(na, 'na', args.save_dir, logger)
    save_dict_as_pkl(ea, 'ea', args.save_dir, logger)
    save_dict_as_pkl(indi, 'individual', args.save_dir, logger)
    save_dict_as_pkl(cumu, 'cumulative', args.save_dir, logger)
