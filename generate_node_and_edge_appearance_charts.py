import argparse

import numpy as np
import pandas as pd
import plotly.express as px

from utils import open_dict_as_pkl


def generate_heat_map(end_episode, appearance_dict, character_a, character_b=None):
    max_season_number = int((end_episode - 1) / 40)
    df_dict = {
        season: [i for i in range((season*40)+1, (season*40)+41)] for season in range(max_season_number+1)
    }
    episode_grid_label = pd.DataFrame(df_dict)
    episode_grid_counter = pd.DataFrame(0, index=range(
        episode_grid_label.shape[0]), columns=episode_grid_label.columns)
    key, attribute, title, label, attribute_format = retrieve_key_and_attribute(character_a, character_b)
    for episode, episode_info in appearance_dict[key].items():
        if episode <= end_episode:
            season_number = int((episode - 1) / 40)
            row_number = episode_grid_label.index[
                episode_grid_label[season_number] == episode][0]
            episode_grid_counter.iloc[row_number, season_number] = episode_info[attribute]
    for col in episode_grid_counter.columns:
        episode_grid_counter[col] = np.where(
            episode_grid_label[col] > end_episode,
            -episode_grid_counter.max().max(), episode_grid_counter[col])
    y_labels = [i+1 for i in episode_grid_counter.columns]
    fig = px.imshow(
        episode_grid_counter.T,
        height=350,
        width=1300,
        color_continuous_scale=['white', 'black', '#23cf77'],
        color_continuous_midpoint=0,
        aspect='auto',
        y=y_labels,
        labels=dict(y='Season'),
        title=title,
    )
    fig.update(
        layout_coloraxis_showscale=False,
    )
    update_fig_layout(fig)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(tickformat='d', tick0=1, dtick=1)
    fig.update_traces(
        text=episode_grid_label.T,
        texttemplate="%{text}",
        hovertemplate='MAG%{text:03}<br>' + f'{label}' + ': %{z:' + f'{attribute_format}' + '} <extra></extra>'
    )
    fig.update_layout(plot_bgcolor="#262730")
    fig.for_each_trace(lambda t: t.update(textfont_color='white',
                                          textfont_family='Baskerville',
                                          hoverlabel_bgcolor='black'))
    return fig


def generate_bar_chart(end_episode, appearance_dict, character_a, character_b=None):
    key, attribute, title, label, attribute_format = retrieve_key_and_attribute(character_a, character_b)
    episode_appearances = appearance_dict[key]
    list_of_episodes = [k for k in range(1, end_episode+1)]
    df = pd.DataFrame(0, index=[label], columns=list_of_episodes)
    for episode, appearance in episode_appearances.items():
        df.loc[label, episode] = appearance[attribute]
    df = df.T
    fig = px.bar(
        df,
        x=list_of_episodes,
        y=label,
        labels=dict(
            x='Episode',
        ),
        title=title,
        color_discrete_sequence=['#23cf77'],
        height=500,
        width=1400,
    )
    update_fig_layout(fig)
    fig.update_layout(plot_bgcolor="#262730") # TODO make this effective
    fig.update_yaxes(showgrid=False, gridwidth=0.05, gridcolor='LightGray')
    fig.update_traces(
        hovertemplate='MAG%{x:03}<br>' + f'{label}' + ': %{y:' + f'{attribute_format}' + '} <extra></extra>'
    )
    return fig


def retrieve_key_and_attribute(character_a, character_b=None):
    if character_b:
        key = tuple(sorted([character_a, character_b]))
        attribute = 'weight'
        title = f'Interactions Between {character_a} and {character_b}'
        label = 'Closeness Score'
        attribute_format = '.0f'
    else:
        key = character_a
        attribute = 'size'
        title = f'Words Spoken by {character_a}'
        label = 'Words Spoken'
        attribute_format = '.3s'
    return key, attribute, title, label, attribute_format


def update_fig_layout(fig):
    fig.update_layout(font_family='Baskerville', font_size=20,
                      hoverlabel=dict(font_family='Baskerville', font_size=14))
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--end_episode', '-E',
        type=int,
        default=160,
        choices=range(1, 161),
        help='Last episode to include in the dict'
    )
    parser.add_argument(
        '--character_a', '-A',
        type=str.upper,
        # choices=[],
        help='A character from The Magnus Archives'
    )
    parser.add_argument(
        '--character_b', '-B',
        type=str.upper,
        default=None,
        # choices=[],
        help='A second character from The Magnus Archives. '
             'If provided, the charts will show the interactions between the '
             'two characters.'
    )
    parser.add_argument(
        '--chart_type', '-C',
        type=str,
        choices=['heatmap', 'bar'],
        default='bar'
    )
    parser.add_argument(
        '--save_dir', '-D',
        type=str,
        default='episode_dicts'
    )
    args = parser.parse_args()
    if args.character_b:
        ad = open_dict_as_pkl('ea', directory=args.save_dir)
    else:
        ad = open_dict_as_pkl('na', directory=args.save_dir)
    if args.chart_type == 'bar':
        func = generate_bar_chart
    else:
        func = generate_heat_map
    figure = func(
        args.end_episode,
        ad,
        args.character_a,
        args.character_b,
    )
    figure.show()
