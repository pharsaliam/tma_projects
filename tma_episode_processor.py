import itertools
import pprint
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from utils import create_logger

CHARACTER_LIST = [
    '\nARCHIVIST\n',
    '\nELIAS\n',
    '\nTIM\n',
    '\nMARTIN\n',
    '\nSASHA\n',
    '\nNOT!SASHA\n',
    '\nMELANIE\n',
    '\nBASIRA\n',
    '\nDAISY\n',
    '\nGETRUDE\n',
    '\nMICHAEL\n',
    '\nHELEN\n',
]


class TMAEpisode:
    def __init__(self, episode_number, logging_level='INFO'):
        self.episode_number = episode_number
        self.logger = create_logger('tma_ep', logging_level=logging_level)
        self.summary = None
        self.transcript = None
        self.characters_in_scenes = None
        self.nodes = None
        self.edges_dict = None

    def __call__(self):
        self.logger.info('Extracting summary and transcript')
        self.extract_summary_and_transcript()
        self.logger.info('Extracting characters in scenes')
        self.extract_characters_in_scenes()
        self.logger.info('Generating nodes and edges dict')
        self.generate_nodes_and_edge_dict()

    def extract_summary_and_transcript(self):
        episode_number_formatted = f'{self.episode_number:03}'
        url = f'''
            https://snarp.github.io/magnus_archives_transcripts/episode/{episode_number_formatted}.html
        '''
        req = Request(
            url
        )
        html_page = urlopen(req)
        soup = BeautifulSoup(html_page, "html.parser")
        html_text = soup.get_text()
        s_start = html_text.find('Summary') + len('Summary')
        s_end = html_text.find('Warning')
        self.summary = html_text[s_start:s_end].strip()
        self.logger.debug(f'Summary of episode: {self.summary}')
        tmarker = '[CLICK]'
        t_start = html_text.find(tmarker) + len(tmarker)
        t_end = html_text.rfind(tmarker)
        self.transcript = html_text[t_start:t_end]

    def extract_characters_in_scenes(self):
        scene_list = self.transcript.split('[CLICK]\n\n[CLICK]')
        self.characters_in_scenes = [
            [c.strip().capitalize() for c in CHARACTER_LIST if c in scene] for
            scene in scene_list
        ]
        self.logger.debug(f'Characters in scenes: {pprint.pformat(self.characters_in_scenes)}')

    def generate_nodes_and_edge_dict(self):
        self.nodes = set(
            [char for char_list in self.characters_in_scenes for char in char_list])
        self.edges_dict = {}
        for cs in self.characters_in_scenes:
            if len(cs) == 2:
                cs = tuple(sorted(cs))
                self.update_individual_edge_dict(cs)
            elif len(cs) > 2:
                cs_combo = [i for i in itertools.combinations(cs, 2)]
                for p in cs_combo:
                    self.update_individual_edge_dict(p)
        self.logger.debug(f'Nodes: {pprint.pformat(self.nodes)}')
        self.logger.debug(f'Edges: {pprint.pformat(self.edges_dict)}')

    def update_individual_edge_dict(self, pair):
        if pair not in self.edges_dict:
            self.edges_dict[pair] = {'weight': 1}
        else:
            self.edges_dict[pair]['weight'] += 1

