import streamlit as st

from utils import open_dict_as_pkl, retrieve_included_edges_and_nodes
from generate_network_charts import TMANetworkChart
from generate_node_and_edge_appearance_charts import generate_bar_chart, generate_heat_map

MAX_EPISODE = 160


def run():
    st.set_page_config(
        page_icon='👁️',
        page_title='TMA Character Appearance and Interaction Visualizations',
        layout='wide',
    )
    st.title('The Magnus Archives Character Appearance and Interaction '
             'Visualizations (up to MAG160)')
    video_file = open('tma_network_1_to_160.mp4', 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)
    st.subheader('View interactions episode by episode')
    episode = st.slider('Select an episode:', 1, MAX_EPISODE)
    # episode = st.number_input('Select an episode', 1, MAX_EPISODE)
    nodes_included, edges_included = retrieve_included_edges_and_nodes()
    chart = TMANetworkChart()
    network_fig, ax1, ax2 = chart.set_up_dual_plot()
    chart.generate_network_chart('individual', episode, ax1,
                                 nodes_included, edges_included)
    chart.generate_network_chart('cumulative', episode, ax2,
                                 nodes_included, edges_included)
    st.pyplot(fig=network_fig)
    st.subheader('View appearances/interactions for each character')
    col1, col2 = st.columns(2)
    with col1:
        character_a = st.selectbox('Select a character', nodes_included)
    with col2:
        b_selections = [None] + [char for char in nodes_included if char != character_a]
        character_b = st.selectbox('Select a second character (opt.)', b_selections)
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


if __name__ == '__main__':
    run()
