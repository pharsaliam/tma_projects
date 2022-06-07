import streamlit as st

from utils import load_config
from B_episode_dicts.save_and_load_dict import open_dict_as_pkl
from C_episode_charts.generate_network_charts import TMANetworkChart
from C_episode_charts.generate_node_and_edge_appearance_charts import (
    generate_bar_chart,
    generate_heat_map,
)
from C_episode_charts.retrieve_en import retrieve_included_edges_and_nodes

CONFIG = load_config()
MAX_EPISODE = CONFIG['MAX_EPISODE']
CHART_DIRECTORY = CONFIG['CHART_DIRECTORY']


def run():
    st.set_page_config(
        page_icon='📼',
        page_title='TMA Character Appearance and Interaction Visualizations',
        layout='wide',
    )
    st.title(
        'The Magnus Archives Character Appearance and Interaction '
        f'Visualizations (up to MAG{MAX_EPISODE})'
    )
    st.markdown(
        '''
        [The Magnus Archives](https://rustyquill.com/show/the-magnus-archives/) 
        is a horror podcast created by Rusty Quill. One of the reasons why I 
        love this podcast is the way it builds out its cast of characters.
        The animation below is a network chart of cumulative character 
        appearances and interactions over the course of the podcast. 
        Watching the video on full screen mode is recommended. 
        
        The size of the character node is proportional to the number of words
        spoken by them, while the width of the edges connecting characters is
        proportional to the "closeness" of their interactions.
        
        See the FAQ section at the end for further details. 
    '''
    )
    video_file = open(
        f'{CHART_DIRECTORY}/tma_network_1_to_{MAX_EPISODE}.mp4', 'rb'
    )
    video_bytes = video_file.read()
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.video(video_bytes)
    st.subheader('View appearances/interactions episode by episode')
    st.markdown(
        '''
        On the left, you can view the character appearances and interactions 
        for the individual episode. On the right are the cumulative 
        interactions after the episode ends (the same image that would be 
        displayed in the video above.) 
    '''
    )
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
        b_selections = [None]
        for edge in edges_included:
            if character_a in edge:
                if character_a == edge[0]:
                    b_selections.append(edge[1])
                else:
                    b_selections.append(edge[0])
        character_b = st.selectbox(
            'Select a second character (opt.)', b_selections
        )
    if character_b:
        appearance_dict = open_dict_as_pkl('ea')
    else:
        appearance_dict = open_dict_as_pkl('na')
    chart_type = st.selectbox('Select a chart type', ['heatmap', 'bar'])
    if chart_type == 'bar':
        func = generate_bar_chart
        chart_entry = 'bar'
    else:
        func = generate_heat_map
        chart_entry = 'square'
    html = func(
        MAX_EPISODE,
        appearance_dict,
        character_a,
        character_b,
    )
    st.markdown(
        f'''
    Clicking on the episode {chart_entry} will open a link to its transcript.
    '''
    )
    st.components.v1.html(html, height=350, width=1350)
    with st.expander('FAQ'):
        st.markdown(
            '''
            ##### Where did you get the data?
            
            Transcript data was sourced from 
            [here](https://snarp.github.io/magnus_archives_transcripts/).
            
            ##### How is character interaction "closeness" calculated?
            
            For interactions between characters, a pair's "closeness" score
            increased by 0.05 for each scene they appeared in together and by
            1 each time they spoke within 5 lines of each other in the scene.
            (A scene is demarcated by the click of the tape recorder.) This
            methodology was inspired by C. Suen, L. Kuenzel, and S. Gil. 2011. 
            *Extraction and analysis of character interaction networks from 
            plays and movies.* Link 
            [here](http://snap.stanford.edu/class/cs224w-2011/proj/laneyk_Finalwriteup_v1.pdf)
            
            ##### Why does character X not appear?
            
            Only characters who have appeared in three or more episodes as of
            MAG160 appear in the chart.  
            
            ##### Are you an avatar of the Web?
            
            No comment. 
        '''
        )


if __name__ == '__main__':
    run()
