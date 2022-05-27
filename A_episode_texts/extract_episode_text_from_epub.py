import re
import pickle

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


if __name__ == '__main__':
    episode_texts_dir = 'A_episode_texts/texts'
    book = epub.read_epub(f'{episode_texts_dir}/the_magnus_archives.epub')
    chapters = [item.get_content() for item in book.get_items() if
                item.get_type() == ebooklib.ITEM_DOCUMENT]
    episode_text_dict = {}
    for chapter in chapters:
        soup = BeautifulSoup(chapter, 'html.parser')
        text = soup.get_text()
        if re.search('^(MAG)+\d\d\d -', text.strip()):
            episode_number = int(text.strip()[3:7])
            episode_text_dict[episode_number] = text.strip()
    with open(f'{episode_texts_dir}/tma_text_from_epub.pkl', 'wb') as outfile:
        pickle.dump(episode_text_dict, outfile)
