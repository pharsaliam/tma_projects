"""
This script creates an animation of multiple network charts for multiple
episodes.

It generates and saves a .mp4 file in the C_episode_charts/charts directory.
"""
import argparse
import os
import sys

from celluloid import Camera
import matplotlib.pyplot as plt

p = os.path.abspath('.')
sys.path.insert(1, p)

from utils import retrieve_included_edges_and_nodes, create_logger
from C_episode_charts.generate_network_charts import TMANetworkChart

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--start_episode', '-S',
        type=int,
        default=1,
        choices=range(1, 161),
        help='First episode to include in the animation'
    )
    parser.add_argument(
        '--end_episode', '-E',
        type=int,
        default=160,
        choices=range(1, 161),
        help='Last episode to include in the animation'
    )
    parser.add_argument(
        '--logging_level', '-L',
        type=str.upper,
        default='info',
        help='Python logging level'
    )
    args = parser.parse_args()
    if args.end_episode < args.start_episode:
        parser.error('Start episode # must be less than end episode #')
    logger = create_logger('animator', logging_level=args.logging_level)
    nodes_included, edges_included = retrieve_included_edges_and_nodes()
    chart = TMANetworkChart()
    plt.rcParams['font.serif'] = ['Baskerville']
    fig, ax = chart.set_up_individual_plot()
    camera = Camera(fig)
    for i in range(args.start_episode, args.end_episode+1):
        chart.generate_network_chart('cumulative', i, ax, nodes_included, edges_included)
        camera.snap()
    animation = camera.animate(interval=300)
    save_location = f'C_episode_charts/charts/tma_network_{args.start_episode}_to_{args.end_episode}.mp4'
    animation.save(save_location)
    logger.info(f'Saved gif to {save_location}')
    plt.close('all')
