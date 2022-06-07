import argparse
import os
import sys

import matplotlib.pyplot as plt
import networkx as nx

p = os.path.abspath('.')
sys.path.insert(1, p)

from utils import create_logger, load_config
from B_episode_dicts.save_and_load_dict import open_dict_as_pkl
from C_episode_charts.retrieve_en import retrieve_included_edges_and_nodes

CONFIG = load_config()
FIXED_POSITIONS = CONFIG['CHART_FIXED_POSITIONS']
DPI = CONFIG['CHART_DPI']
MAX_EPISODE = CONFIG['MAX_EPISODE']
DICT_DIRECTORY = CONFIG['DICT_DIRECTORY']


class TMANetworkChart:
    """
    A class used to represent an episode network chart.

    Attributes
    ---
    episode_dict_dict: dict
        Nested dictionary containing both the individual and cumulative
        episode dicts
    logger: a logging.Logger object
    """

    def __init__(self, directory=DICT_DIRECTORY, logging_level='INFO'):
        """
        :param directory: Directory from which to retrieve the individual
            and cumulative episode dicts
        :type directory: str
        :param logging_level: A standard Python logging level
            (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        :type logging_level: str
        """
        individual_episode_dict = open_dict_as_pkl(
            'individual', directory=directory
        )
        cumulative_episode_dict = open_dict_as_pkl(
            'cumulative', directory=directory
        )
        self.episode_dict_dict = {
            'individual': individual_episode_dict,
            'cumulative': cumulative_episode_dict,
        }
        self.logger = create_logger('TMA_chart', logging_level=logging_level)

    @staticmethod
    def set_up_individual_plot(figsize=(10, 10), dpi=DPI):
        """
        Set configuration for creating an individual plot of either an
        individual or cumulative network chart
        :param figsize: Width, height in inches.
        :type figsize: (float, float)
        :param dpi: The resolution of the figure in dots-per-inch
        :type dpi: float
        :return: matplotlib.figure.Figure object, matplotlib.axes.Axes object
        :rtype: matplotlib.figure.Figure object, matplotlib.axes.Axes object
        """
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor='#0E1117')
        ax.set_facecolor('black')
        ax.set_xlim([-1.2, 1.1])
        ax.set_ylim([-1.1, 1.2])
        fig.tight_layout(pad=0.75)
        return fig, ax

    @staticmethod
    def set_up_dual_plot(figsize=(20, 10), dpi=DPI):
        """
        Set configuration for creating side-by-side plots for individual and
        cumulative network charts
        :param figsize: Width, height in inches.
        :type figsize: (float, float)
        :param dpi: The resolution of the figure in dots-per-inch
        :type dpi: float
        :return: matplotlib.figure.Figure object, matplotlib.axes.Axes array
        :rtype: matplotlib.figure.Figure object, matplotlib.axes.Axes array
        """
        fig, (ax1, ax2) = plt.subplots(
            1,
            2,
            sharex=True,
            sharey=True,
            figsize=figsize,
            dpi=dpi,
            facecolor='#0E1117',
        )
        for axi in [ax1, ax2]:
            axi.set_facecolor('black')
            axi.set_xlim([-1.2, 1.1])
            axi.set_ylim([-1.1, 1.2])
        fig.tight_layout(pad=0.75)
        return fig, ax1, ax2

    def generate_network_chart(
        self,
        episode_dict_type,
        episode_number,
        ax,
        nodes_incl,
        edges_incl,
        save=False,
    ):
        """
        Plots an individual or cumulative network chart for a particular
        episode
        :param episode_dict_type: 'individual' or 'cumulative'
        :type episode_dict_type: str
        :param episode_number: episode number
        :type episode_number: int
        :param ax: the matplotlib.axes.Axes object on which to plot
        :type ax: matplotlib.axes.Axes object
        :param nodes_incl: Nodes to include in the chart
        :type nodes_incl: list
        :param edges_incl: Edges to include in the chart
        :type edges_incl: list
        :param save: Whether or not to save the figure
        :type save: bool
        :return: None
        :rtype: None
        """
        assert episode_dict_type in ('individual', 'cumulative')
        episode_dict = self.episode_dict_dict[episode_dict_type]
        nd = episode_dict[episode_number]['nodes_dict']
        ed = episode_dict[episode_number]['edges_dict']
        nodes = [(k, v) for k, v in nd.items() if k in nodes_incl]
        edges = [(*k, v) for k, v in ed.items() if k in edges_incl]
        g = nx.Graph()
        g.add_nodes_from(nodes)
        g.add_edges_from(edges)
        pos = FIXED_POSITIONS
        font = {
            'color': 'white',
            'fontsize': 18,
            'family': 'serif',
            'fontweight': 'bold',
        }
        if episode_dict_type == 'cumulative':
            node_size = [s[1]['size'] / 40 for s in g.nodes.data()]
            edge_weights = [g[u][v]['weight'] / 100 for u, v in g.edges]
        else:
            node_size = [s[1]['size'] / 20 for s in g.nodes.data()]
            edge_weights = [g[u][v]['weight'] / 50 for u, v in g.edges]
        nx.draw_networkx_nodes(
            g,
            pos,
            ax=ax,
            node_size=node_size,
            node_color='#1a9340',
            edgecolors='#126840',
        )
        nx.draw_networkx_edges(
            g, pos, ax=ax, width=edge_weights, alpha=0.5, edge_color='#23cf77'
        )
        nx.draw_networkx_labels(
            g, pos, ax=ax, font_color=font['color'], font_family=font['family']
        )
        ax.text(
            0.5,
            0.97,
            f"MAG{episode_number:03} ({episode_dict_type.upper()})",
            ha='center',
            va='center',
            fontdict=font,
            transform=ax.transAxes,
            bbox=dict(facecolor='#1a9340', alpha=0.5),
        )
        self.logger.info(
            f'Plotted {episode_dict_type} network chart for MAG{episode_number:03}'
        )
        if save:
            save_location = f'MAG{episode_number:03}_{episode_dict_type}.png'
            plt.savefig(save_location, dpi=DPI)
            self.logger.info(f'Saved chart to {save_location}')
        return None


if __name__ == '__main__':
    plt.rcParams['font.serif'] = ['Baskerville']
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--episode',
        '-E',
        type=int,
        default=1,
        choices=range(1, MAX_EPISODE + 1),
        help='Episode to plot',
    )
    parser.add_argument(
        '--save_dir',
        '-D',
        type=str,
        default=DICT_DIRECTORY,
        help='Directory where individual and cumulative dicts are saved',
    )
    args = parser.parse_args()
    nodes_included, edges_included = retrieve_included_edges_and_nodes()
    chart = TMANetworkChart(directory=args.save_dir)
    fig, ax1, ax2 = chart.set_up_dual_plot()
    chart.generate_network_chart(
        'individual', args.episode, ax1, nodes_included, edges_included
    )
    chart.generate_network_chart(
        'cumulative', args.episode, ax2, nodes_included, edges_included
    )
    plt.show()
