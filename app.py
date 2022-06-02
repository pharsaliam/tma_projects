import streamlit as st

from utils import open_dict_as_pkl, retrieve_included_edges_and_nodes
from C_episode_charts.generate_network_charts import TMANetworkChart
from C_episode_charts.generate_node_and_edge_appearance_charts import (
    generate_bar_chart,
    generate_heat_map,
)

MAX_EPISODE = 160


def run():
    st.set_page_config(
        page_icon='📼',
        page_title='TMA Character Appearance and Interaction Visualizations',
        layout='wide',
    )
    st.title(
        'The Magnus Archives Character Appearance and Interaction '
        'Visualizations (up to MAG160)'
    )
    st.markdown(
        '''
        [The Magnus Archives](https://rustyquill.com/show/the-magnus-archives/) 
        is a horror podcast created by Rusty Quill. One of the reasons why I 
        love this podcast is the way it builds out its cast of characters.
        The animation below is a network chart of cumulative character 
        appearances and interactions over the course of the podcast. 
        
        The size of the character node is proportional to the number of words
        spoken by them, while the width of the edges connecting characters is
        proportional to the "closeness" of their interactions.
        
        See the FAQ section at the end for details. 
    '''
    )
    video_file = open('C_episode_charts/charts/tma_network_1_to_160.mp4', 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)
    st.subheader('View interactions episode by episode')
    st.markdown(
        '''
        On the left, you can view the character interactions for the
        individual episode. On the right are the cumulative interactions after
        the episode.  
    '''
    )
    # episode = st.slider('Select an episode:', 1, MAX_EPISODE)
    episode = st.number_input(
        f'Select an episode (1 to {MAX_EPISODE})', 1, MAX_EPISODE
    )
    nodes_included, edges_included = retrieve_included_edges_and_nodes()
    chart = TMANetworkChart()
    network_fig, ax1, ax2 = chart.set_up_dual_plot()
    chart.generate_network_chart(
        'individual', episode, ax1, nodes_included, edges_included
    )
    chart.generate_network_chart(
        'cumulative', episode, ax2, nodes_included, edges_included
    )
    st.pyplot(fig=network_fig)
    st.subheader('View appearances/interactions for each character')
    st.markdown(
        '''
        Select a character to view their appearances over the course of the
        show. If you select a second character, you can view the interactions
        between the pair. 
    '''
    )
    col1, col2 = st.columns(2)
    with col1:
        character_a = st.selectbox('Select a character', nodes_included)
    with col2:
        b_selections = [None] + [
            char for char in nodes_included if char != character_a
        ]
        character_b = st.selectbox(
            'Select a second character (opt.)', b_selections
        )
    chart_type = st.selectbox('Select a chart type', ['heatmap', 'bar'])
    if character_b:
        appearance_dict = open_dict_as_pkl('ea')
    else:
        appearance_dict = open_dict_as_pkl('na')
    if chart_type == 'bar':
        func = generate_bar_chart
    else:
        func = generate_heat_map
    appearance_figure = func(
        MAX_EPISODE,
        appearance_dict,
        character_a,
        character_b,
    )
    st.plotly_chart(appearance_figure)
    with st.expander('FAQ'):
        st.markdown(
            '''
            ##### Where did you get the data?
            
            Transcript data was sourced from 
            [here](https://snarp.github.io/magnus_archives_transcripts/).
            
            ##### How is character "closeness" calculated?
            
            For interactions between characters, a pair's "closeness" score
            increased by 0.05 for each scene they appeared in together and by
            2 each time they spoke within 5 lines of each other in the scene.
            (A scene is demarcated by the click of the tape recorder.)  
            
            ##### Why does X character not appear?
            
            Only characters who had appeared in three or more episodes as of
            MAG160 appear in the chart.  
            
            ##### Are you an avatar of the Web?
            
            No comment. 
        '''
        )


if __name__ == '__main__':
    run()
