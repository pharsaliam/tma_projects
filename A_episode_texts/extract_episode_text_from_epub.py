"""
This script parses an ebook of The Magnus Archives Transcripts to separate
episode texts by episode.

It assumes that an .epub files containing all the transcripts is saved as
A_episode_texts/texts/the_magnus_archives.epub.

It generates and saves the file A_episode_texts/texts/tma_text_from_epub.pkl.
"""
import re
import pickle

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

from utils import load_config

CONFIG = load_config()
TEXT_DIRECTORY = CONFIG['TEXT_DIRECTORY']

if __name__ == '__main__':
    book = epub.read_epub(f'{TEXT_DIRECTORY}/the_magnus_archives.epub')
    chapters = [
        item.get_content()
        for item in book.get_items()
        if item.get_type() == ebooklib.ITEM_DOCUMENT
    ]
    episode_text_dict = {}
    for chapter in chapters:
        soup = BeautifulSoup(chapter, 'html.parser')
        text = soup.get_text()
        if re.search('^(MAG)+\d\d\d -', text.strip()):
            episode_number = int(text.strip()[3:7])
            episode_text_dict[episode_number] = text.strip()
    with open(f'{TEXT_DIRECTORY}/tma_text_from_epub.pkl', 'wb') as outfile:
        pickle.dump(episode_text_dict, outfile)
