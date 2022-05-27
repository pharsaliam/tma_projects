# The Magnus Archives Character Appearance and Interaction Visualizations

Here is a Streamlit app for visualizing character interactions and appearances over time in [The Magnus Archives](https://rustyquill.com/show/the-magnus-archives/), as well as the code for generating the requisite files and animations. It currently goes up to MAG160 (because that's as far as I've listened :smile:).

[Here](https://share.streamlit.io/pharsaliam/tma_projects/main/app.py) is a link to the app.

## Instructions
Here are instructions for recreating the interim files used by the app (assuming you've cloned the repo and installed all the packages in `requirements.txt`.
1. Download an ebook of the transcripts [here](https://snarp.github.io/magnus_archives_transcripts/) and save it to `A_episode_texts/texts/the_magnus_archives.epub`. 
2. Run `$ python3 A_episode_texts/extract_episode_text_from_epub.py` to parse the ebook by episode and extract the transcripts. This will generate the file `A_episode_texts/texts/tma_text_from_epub.pkl`.    
3. Run `$ python3 B_episode_dicts/generate_episode_dicts.py -E <INPUT DESIRED END EPISODE>` (e.g., `python3 B_episode_dicts/generate_episode_dicts.py -E 160`) to create the dicts containing information about character appearance/interactions. This will generate four files (`individual.pkl`, `cumulative.pkl`, `ea.pkl`, `na.pkl`) in the directory `B_episode_dicts/dicts`.
4. Run `$ C_episode_charts/animate_network_chart.py -E <INSERT SAME END EPISODE AS STEP 3>` to create the animation of the network chart over time. This will generate the video `C_episode_charts/charts/tma_network_1_to_<END EPISODE>.mp4`.
5. Run `$ streamlit run app.py` to view the app locally. 