import argparse
import sys
import os
import re
import webbrowser
import tempfile

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot

p = os.path.abspath('.')
sys.path.insert(1, p)

from utils import load_config
from B_episode_dicts.save_and_load_dict import open_dict_as_pkl

CONFIG = load_config()
MAX_EPISODE = CONFIG['MAX_EPISODE']
DICT_DIRECTORY = CONFIG['DICT_DIRECTORY']
CHART_BY_CHARACTER_DIMENSIONS = CONFIG['CHART_BY_CHARACTER_DIMENSIONS']


def generate_heat_map(
    end_episode, appearance_dict, character_a, character_b=None
):
    """
    Generates a HTML string representing a heatmap using plotly.imshow() to
    show which episodes characters appear or interact and the extent of that
    appearance/interaction
    :param end_episode: Last episode to include in chart
    :type end_episode: int
    :param appearance_dict: Either a node or edge appearance dict where the key
        is a node/edge and the values contain episode appearance/interaction
        attributes
    :type appearance_dict: dict
    :param character_a: A character from The Magnus Archives
    :type character_a: str
    :param character_b: A second character from The Magnus Archives.
        If provided, the chart will show the interactions between the two
        characters. If not, the chart will show the appearances of character_a
    :type character_b: str
    :return: HTML string representing a plotly.graph_objects.Figure with the
        heatmap  plotted on it
    :rtype: str
    """
    max_season_number = int((end_episode - 1) / 40)
    df_dict = {
        season: [i for i in range((season * 40) + 1, (season * 40) + 41)]
        for season in range(max_season_number + 1)
    }
    episode_grid_label = pd.DataFrame(df_dict)
    episode_grid_counter = pd.DataFrame(
        0,
        index=range(episode_grid_label.shape[0]),
        columns=episode_grid_label.columns,
    )
    episode_grid_url = episode_grid_label.copy()
    for col in episode_grid_url.columns:
        episode_grid_url[col] = [
            f'https://snarp.github.io/magnus_archives_transcripts/episode/'
            + f'{a:03}.html'
            for a in episode_grid_url[col]
        ]
    key, attribute, title, label, attribute_format = retrieve_key_and_attribute(
        character_a, character_b
    )
    for episode, episode_info in appearance_dict[key].items():
        if episode <= end_episode:
            season_number = int((episode - 1) / 40)
            row_number = episode_grid_label.index[
                episode_grid_label[season_number] == episode
            ][0]
            episode_grid_counter.iloc[row_number, season_number] = episode_info[
                attribute
            ]
    for col in episode_grid_counter.columns:
        episode_grid_counter[col] = np.where(
            episode_grid_label[col] > end_episode,
            -episode_grid_counter.max().max(),
            episode_grid_counter[col],
        )
    y_labels = [i + 1 for i in episode_grid_counter.columns]
    fig = px.imshow(
        episode_grid_counter.T,
        height=CHART_BY_CHARACTER_DIMENSIONS['HEIGHT'],
        width=CHART_BY_CHARACTER_DIMENSIONS['WIDTH'],
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
    )
    fig.update(
        data=[
            {
                'customdata': episode_grid_url.T,
                'hovertemplate': 'MAG%{text:03}<br>'
                + f'{label}'
                + ': %{z:'
                + f'{attribute_format}'
                + '} <extra></extra>',
            }
        ]
    )
    fig.for_each_trace(
        lambda t: t.update(
            textfont_color='white',
            textfont_family='Baskerville',
            hoverlabel_bgcolor='black',
        )
    )
    html_str = fig_to_html(fig)

    return html_str


def generate_bar_chart(
    end_episode, appearance_dict, character_a, character_b=None
):
    """
    Generates a bar chart using plotly.bar() to show which episodes characters
    appear or interact and the extent of that appearance/interaction
    :param end_episode: Last episode to include in chart
    :type end_episode: int
    :param appearance_dict: Either a node or edge appearance dict where the key
        is a node/edge and the values contain episode appearance/interaction
        attributes
    :type appearance_dict: dict
    :param character_a: A character from The Magnus Archives
    :type character_a: str
    :param character_b: A second character from The Magnus Archives.
        If provided, the chart will show the interactions between the two
        characters. If not, the chart will show the appearances of character_a
    :type character_b: str
    :return: HTML string representing a plotly.graph_objects.Figure with the
        bar chart plotted on it
    :rtype: str
    """
    key, attribute, title, label, attribute_format = retrieve_key_and_attribute(
        character_a, character_b
    )
    episode_appearances = appearance_dict[key]
    list_of_episodes = [k for k in range(1, end_episode + 1)]
    urls = [
        f'https://snarp.github.io/magnus_archives_transcripts/episode/'
        + f'{a:03}.html'
        for a in list_of_episodes
    ]
    df = pd.DataFrame(0, index=[label], columns=[list_of_episodes])
    for episode, appearance in episode_appearances.items():
        df.loc[label, episode] = appearance[attribute]
    df = df.T
    df['url'] = urls
    fig = px.bar(
        df,
        x=list_of_episodes,
        y=label,
        labels=dict(
            x='Episode',
        ),
        title=title,
        color_discrete_sequence=['#23cf77'],
        height=CHART_BY_CHARACTER_DIMENSIONS['HEIGHT'],
        width=CHART_BY_CHARACTER_DIMENSIONS['WIDTH'],
        custom_data=['url'],
    )
    update_fig_layout(fig)
    fig.update_yaxes(showgrid=False, tickformat='.1s')
    fig.update_traces(
        hovertemplate='MAG%{x:03}<br>'
        + f'{label}'
        + ': %{y:'
        + f'{attribute_format}'
        + '} <extra></extra>'
    )
    html_str = fig_to_html(fig)

    return html_str


def fig_to_html(fig):
    """
    Converts a figure to an HTML string with functionality that opens a url.
    This assumes you have stored the url to open in the customdata of a figure
    :param fig: a figure with data already plotted on it
    :type fig: plotly.graph_objects.Figure
    :return: HTML string representing a plotly.graph_objects.Figure with the
        bar chart plotted on it
    :rtype: str
    """
    fig = go.Figure(data=fig.data, layout=fig.layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=True)

    # Get id of html div element that looks like
    # <div id="301d22ab-bfba-4621-8f5d-dc4fd855bb33" ... >
    res = re.search('<div id="([^"]*)"', plot_div)
    div_id = res.groups()[0]

    # Build JavaScript callback for handling clicks
    # and opening the URL in the trace's customdata
    js_callback = """
        <script>
        var plot_element = document.getElementById("{div_id}");
        plot_element.on('plotly_click', function(data){{
            console.log(data);
            var point = data.points[0];
            if (point) {{
                console.log(point.customdata);
                window.open(point.customdata);
            }}
        }})
        </script>
        """.format(
        div_id=div_id
    )

    # Build HTML string
    html_str = """
        <html>
        <body>
        {plot_div}
        {js_callback}
        </body>
        </html>
        """.format(
        plot_div=plot_div, js_callback=js_callback
    )
    return html_str


def retrieve_key_and_attribute(character_a, character_b=None):
    """
    Returns keys and attributes depending on whether a second character is
    provided (plotting edges) or not (plotting nodes)
    :param character_a: A character from The Magnus Archives
    :type character_a: str
    :param character_b: A second character from The Magnus Archives.
        If provided, the chart will show the interactions between the two
        characters. If not, the chart will show the appearances of character_a
    :type character_b: str
    :return:
        1. key for looking up item in node/edge appearance dict
        2. appearance/interaction attribute name
        3. title for chart
        4. appearance/interaction attribute label
        5. attribute number format (d3-format option)
    :rtype: tuple or str, str, str, str, str
    """
    if character_b:
        key = tuple(sorted([character_a, character_b]))
        attribute = 'weight'
        title = f'Interactions Between {character_a} and {character_b}'
        label = 'Interaction Score'
        attribute_format = '.0f'
    else:
        key = character_a
        attribute = 'size'
        title = f'Words Spoken by {character_a}'
        label = 'Words Spoken'
        attribute_format = '.3s'
    return key, attribute, title, label, attribute_format


def update_fig_layout(fig):
    """
    Update plotly.graph_objects.Figure layout
    :param fig: plotly.graph_objects.Figure
    :type fig: plotly.graph_objects.Figure
    :return: None
    :rtype: None
    """
    fig.update_layout(
        font_family='Baskerville',
        font_size=20,
        font_color='white',
        hoverlabel=dict(font_family='Baskerville', font_size=14),
        plot_bgcolor="#262730",
        paper_bgcolor="#262730",
    )
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--end_episode',
        '-E',
        type=int,
        default=MAX_EPISODE,
        choices=range(1, MAX_EPISODE + 1),
        help='Last episode to include in the dict',
    )
    parser.add_argument(
        '--character_a',
        '-A',
        type=str.upper,
        # choices=[],
        help='A character from The Magnus Archives',
    )
    parser.add_argument(
        '--character_b',
        '-B',
        type=str.upper,
        default=None,
        # choices=[],
        help='A second character from The Magnus Archives. '
        'If provided, the charts will show the interactions between the '
        'two characters.',
    )
    parser.add_argument(
        '--chart_type',
        '-C',
        type=str,
        choices=['heatmap', 'bar'],
        default='bar',
    )
    parser.add_argument('--save_dir', '-D', type=str, default=DICT_DIRECTORY)
    args = parser.parse_args()
    if args.character_b:
        ad = open_dict_as_pkl('ea', directory=args.save_dir)
    else:
        ad = open_dict_as_pkl('na', directory=args.save_dir)
    if args.chart_type == 'bar':
        func = generate_bar_chart
    else:
        func = generate_heat_map
    html = func(
        args.end_episode,
        ad,
        args.character_a,
        args.character_b,
    )
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
        url = 'file://' + f.name
        f.write(html)
    webbrowser.open(url)
