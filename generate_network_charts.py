import pickle
import argparse

import matplotlib.pyplot as plt
import networkx as nx

from utils import DICT_TYPES, MIN_EPISODE_APPEARANCES

FIXED_POSITIONS = {
    'MARTIN': [-0.50785913437188222, 0.08477362049934986],
    'ELIAS': [0.494622046596421, -0.8496412076926273],
    'ARCHIVIST': [0.39497082023195323, 0.08477362049934986],
    'SASHA': [-0.9525321492929766, 0.2829317568689825],
    'MELANIE': [0.8879192021330844, -0.35028543487470515],
    'TIM': [-0.6407332236883497, 0.7039490847522484],
    'BREEKON': [-0.6640046638082411, -0.8194784186915571],
    'MICHAEL': [0.40920022617553936, 0.9530705335491978],
    'BASIRA': [0.8374579409643357, 0.36115163173876225],
    'GERTRUDE': [-0.3101090003330547, -0.9487132319098708],
    'JULIA': [0.0648092656994219, -0.9586427617163064],
    'HOPE': [-0.9386163812554091, -0.5262024764971592],
    'DAISY': [-0.18843498813231419, 0.9943061532302655],
    'GEORGIE': [0.6372042049249488, 0.6649350411778464],
    'PETER': [0.0587236938644669, 0.7914881431925871],
    'HELEN': [0.8316638715482926, -0.00243600699759311],
    'TREVOR': [-1.0, -0.12557792368338694]
}
DPI = 150
parser = argparse.ArgumentParser()
parser.add_argument(
    '--episode', '-E',
    type=int,
    default=1,
    choices=range(1, 161),
    help='Episode to plot'
)
args = parser.parse_args()


def open_dict_as_pkl(dict_type, directory='episode_dicts'):
    assert dict_type in DICT_TYPES
    with open(f'{directory}/{dict_type}.pkl', 'rb') as f:
        ed = pickle.load(f)
    return ed


def retrieve_included_edges_and_nodes(node_appearance_dict, edges_appearance_dict, minimum_episode_appearances=MIN_EPISODE_APPEARANCES):
    nodes_incl = [node for node, node_appearances in node_appearance_dict.items() if len(node_appearances) > minimum_episode_appearances]
    edges_incl = [edge for edge, edge_appearance in edges_appearance_dict.items() if
                  (edge[0] in nodes_incl) & (edge[1] in nodes_incl)]
    return nodes_incl, edges_incl


def set_up_individual_plot():
    fig, ax = plt.subplots(figsize=(10, 10), dpi=DPI)
    ax.set_facecolor('black')
    ax.set_xlim([-1.2, 1.1])
    ax.set_ylim([-1.1, 1.2])
    fig.tight_layout(pad=0.75)
    return fig, ax

def set_up_dual_plot():
    fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(20, 10), dpi=DPI)
    for axi in [ax1, ax2]:
        axi.set_facecolor('black')
        axi.set_xlim([-1.2, 1.1])
        axi.set_ylim([-1.1, 1.2])
    fig.tight_layout(pad=0.75)
    return fig, ax1, ax2


def generate_network_chart(episode_dict_type, episode_dict_dict, episode_number, ax, nodes_incl, edges_incl, save=False):
    assert episode_dict_type in ('individual', 'cumulative')
    episode_dict = episode_dict_dict[episode_dict_type]
    nd = episode_dict[episode_number]['nodes_dict']
    ed = episode_dict[episode_number]['edges_dict']
    nodes = [(k, v) for k, v in nd.items() if k in nodes_incl]
    edges = [(*k, v) for k, v in ed.items() if k in edges_incl]
    g = nx.Graph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    pos = FIXED_POSITIONS
    font = {'color': 'white', 'fontsize': 18, 'family': 'Baskerville',
            'fontweight': 'bold'}
    if episode_dict_type == 'cumulative':
        node_size = [s[1]['size'] / 40 for s in g.nodes.data()]
        edge_weights = [g[u][v]['weight'] / 100 for u, v in g.edges]
    else:
        node_size = [s[1]['size'] / 20 for s in g.nodes.data()]
        edge_weights = [g[u][v]['weight'] / 50 for u, v in g.edges]
    nx.draw_networkx_nodes(g, pos, ax=ax, node_size=node_size,
                                   node_color='#1a9340', edgecolors='#126840')
    nx.draw_networkx_edges(g, pos, ax=ax, width=edge_weights,
                                   alpha=0.5, edge_color='#23cf77')
    nx.draw_networkx_labels(g, pos, ax=ax, font_color=font['color'],
                                     font_family=font['family'])
    ax.text(
        0.5, 0.97,
        f"MAG{episode_number:03} ({episode_dict_type.upper()})",
        ha='center',
        va='center',
        fontdict=font,
        transform=ax.transAxes,
        bbox=dict(facecolor='#1a9340', alpha=0.5)
    )
    if save:
        plt.savefig(f'MAG{episode_number:03}_{episode_dict_type}.png', dpi=DPI)
    return None


if __name__ == '__main__':
    individual_episode_dict = open_dict_as_pkl('individual')
    cumulative_episode_dict = open_dict_as_pkl('cumulative')
    ea = open_dict_as_pkl('ea')
    na = open_dict_as_pkl('na')
    episode_dict_dict = {
        'individual': individual_episode_dict,
        'cumulative': cumulative_episode_dict
    }
    nodes_included, edges_included = retrieve_included_edges_and_nodes(na, ea)
    fig, ax1, ax2 = set_up_dual_plot()
    generate_network_chart('individual', episode_dict_dict, args.episode, ax1, nodes_included, edges_included)
    generate_network_chart('cumulative', episode_dict_dict, args.episode, ax2, nodes_included, edges_included)
    plt.show()
