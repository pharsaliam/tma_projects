import itertools
import pprint
import pickle
import re

from utils import create_logger

CHARACTER_LIST = [
    '\nARCHIVIST\n',
    '\nELIAS\n',
    '\nELIAS (JONAH)\n',
    '\nTIM\n',
    '\nMARTIN\n',
    '\nSASHA\n',
    '\nNOT!SASHA\n',
    '\nMELANIE\n',
    '\nBASIRA\n',
    '\nDAISY\n',
    '\nGERTRUDE\n',
    '\nGEORGIE\n',
    '\nMICHAEL\n',
    '\nHELEN\n',
    '\nPETER\n',
]

CHARACTER_CONSOLIDATION_DICT = {
    '\nELIAS (JONAH)\n': '\nELIAS\n'
}


class TMAEpisode:
    def __init__(self, episode_number, logging_level='INFO'):
        self.number = episode_number
        self.logger = create_logger('tma_ep', logging_level=logging_level)
        self.transcript = None
        self.characters_in_scenes = None
        self.nodes_dict = None
        self.edges_dict = None

    def __call__(self):
        self.logger.info('Extracting summary and transcript')
        self.extract_transcript()
        self.logger.info('Extracting characters in scenes')
        self.extract_characters_in_scenes()
        self.logger.info('Generating nodes dict and edges dict')
        self.generate_nodes_and_edges_dict()

    def extract_transcript(self):
        with open('episode_texts/tma_text_from_epub.pkl', 'rb') as f:
            all_episode_texts = pickle.load(f)
        html_text = all_episode_texts[self.number]
        tmarker = '[CLICK]'
        t_start = html_text.find(tmarker) + len(tmarker)
        t_end = html_text.rfind(tmarker)
        self.transcript = html_text[t_start:t_end]

    def extract_characters_in_scenes(self):
        for k, v in CHARACTER_CONSOLIDATION_DICT.items():
            self.transcript = self.transcript.replace(k, v)
        scene_list = re.split(r'\[TAPE CLICKS OFF.\][\n][\n][^\n][A-Za-z0-9 _.,!"\'\’\]]*[\n]\[TAPE CLICKS ON.\]|\[CLICK\]\n\n\[CLICK\]', self.transcript)
        self.characters_in_scenes = [
            [c.strip() for c in CHARACTER_LIST if c in scene] for
            scene in scene_list
        ]
        self.logger.debug(f'Characters in scenes: {pprint.pformat(self.characters_in_scenes)}')

    def generate_nodes_and_edges_dict(self):
        self.nodes_dict = {
            char: {'size': 1} for char_list in self.characters_in_scenes for char in char_list
        }
        self.edges_dict = {}
        for cs in self.characters_in_scenes:
            if len(cs) == 2:
                cs = tuple(sorted(cs))
                self.update_individual_edge_dict(cs)
            elif len(cs) > 2:
                cs_combo = [i for i in itertools.combinations(cs, 2)]
                for p in cs_combo:
                    p = tuple(sorted(p))
                    self.update_individual_edge_dict(p)
        self.logger.debug(f'Nodes: {pprint.pformat(self.nodes_dict)}')
        self.logger.debug(f'Edges: {pprint.pformat(self.edges_dict)}')

    def update_individual_edge_dict(self, pair):
        if pair not in self.edges_dict:
            self.edges_dict[pair] = {'weight': 1}
        # Uncomment next two lines if we ever want to count
        # characters who interact in multiple scenes per episode multiple times
        # else:
        #     self.edges_dict[pair]['weight'] += 1

