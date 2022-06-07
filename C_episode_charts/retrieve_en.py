from utils import load_config
from B_episode_dicts.save_and_load_dict import open_dict_as_pkl

CONFIG = load_config()
MIN_EPISODE_APPEARANCES = CONFIG['MIN_EPISODE_APPEARANCES']
DICT_DIRECTORY = CONFIG['DICT_DIRECTORY']


def retrieve_included_edges_and_nodes(
    directory=DICT_DIRECTORY,
    minimum_episode_appearances=MIN_EPISODE_APPEARANCES,
):
    """
    Retrieve a list of nodes that have hit a minimum episode appearance number
    and the edges relevant to that list of nodes
    :param directory: Directory in which node or edge appearance dict is saved
        as a .pkl file
    :type directory: str
    :param minimum_episode_appearances: Minimum number of episodes node must
        appear in to be included
    :type minimum_episode_appearances: int
    :return: list of included nodes, list of included edges
    :rtype: list, list
    """
    node_appearance_dict = open_dict_as_pkl('na', directory=directory)
    edges_appearance_dict = open_dict_as_pkl('ea', directory=directory)
    nodes_incl = [
        node
        for node, node_appearances in node_appearance_dict.items()
        if len(node_appearances) >= minimum_episode_appearances
    ]
    edges_incl = [
        edge
        for edge, edge_appearance in edges_appearance_dict.items()
        if (edge[0] in nodes_incl) & (edge[1] in nodes_incl)
    ]
    return nodes_incl, edges_incl
