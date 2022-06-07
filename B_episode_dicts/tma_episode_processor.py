import itertools
import pprint
import pickle
import re
from collections import defaultdict

from utils import create_logger, load_config

CONFIG = load_config()

CHARACTER_CONSOLIDATION_DICT = CONFIG['CHARACTER_CONSOLIDATION_DICT']
CHARACTER_CONSOLIDATION_DICT_2 = {
    '\nMAGNUS\n': '\nELIAS\n',
    '\nJOHN\n': '\nARCHIVIST\n',
}
LINES_NEEDED_FOR_CLOSENESS = CONFIG['LINES_NEEDED_FOR_CLOSENESS']
MIN_CLOSENESS = CONFIG['MIN_CLOSENESS']
TEXT_DIRECTORY = CONFIG['TEXT_DIRECTORY']


class TMAEpisode:
    """
    A class used to represent an episode.

    Attributes
    ---
    number : int
        Episode number
    logger : a logging.Logger object
    transcript: str
        Episode transcript (stripped of title, summary, notes etc.)
    character_info_in_scenes: dict
        Nested dictionary where key is a scene number and value is a dictionary
        of characters, their word counts, and line appearances in the scene
    nodes_dict: dict
        Nested dictionary where key is a character in the episode and value is
        a dictionary of their attributes in the episode (currently just total
        words spoken, labeled "size" since it will be the size of the node)
    edges_dict: dict
        Nested dictionary where key is a pair of characters who appear in at
        least one scene together in the episode and value is a dictionary
        of their interaction attributes (currently just the "closeness" of
        interaction, labeled "weight" since it will be the weight of the edge)
    """

    def __init__(self, episode_number, logging_level='INFO'):
        """
        :param episode_number: Episode number
        :type episode_number: int
        :param logging_level: A standard Python logging level
            (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        :type logging_level: str
        """
        self.number = episode_number
        self.logger = create_logger('tma_ep', logging_level=logging_level)
        self.transcript = None
        self.character_info_in_scenes = {}
        self.nodes_dict = {}
        self.edges_dict = {}

    def __call__(self):
        self.logger.info(f'{self.number} Extracting transcript')
        self.extract_transcript()
        self.clean_up_character_names()
        self.logger.info(f'{self.number} Extracting character info in scene')
        self.extract_character_info_in_scenes()
        self.logger.info(f'{self.number} Generating nodes dict and edges dict')
        self.generate_nodes_and_edges_dict()

    def extract_transcript(self):
        """
        Strips episode text of title, summary, and notes to extract transcript
        :return: None
        :rtype: None
        """
        with open(f'{TEXT_DIRECTORY}/tma_text_from_epub.pkl', 'rb') as f:
            all_episode_texts = pickle.load(f)
        html_text = all_episode_texts[self.number]
        tmarker1 = '[CLICK'
        tmarker2 = '[TAPE CLICKS'
        tmarker3 = 'End supplement'
        t_start_l = [html_text.find(tmarker1), html_text.find(tmarker2)]
        t_end_l = [
            html_text.rfind(tmarker1),
            html_text.rfind(tmarker2),
            html_text.find(tmarker3),
        ]
        t_start_l = [i for i in t_start_l if i > 0]
        t_end_l = [i for i in t_end_l if i > 0]
        t_start = min(t_start_l + [0])
        t_end = max(t_end_l + [-1])
        self.transcript = html_text[t_start:t_end]
        return None

    def clean_up_character_names(self):
        """
        Removing parenthetical after character names in transcript
        (e.g., "ELIAS (JONAH)" becomes "ELIAS"
        :return: None
        :rtype: None
        """
        lines = self.transcript.split('\n')
        new_lines = []
        for line in lines:
            if re.match('^[A-Z]* \([A-Z]*\)$', line):
                split = line.split()
                new_lines.append(split[0])
            else:
                new_lines.append(line)
        self.transcript = '\n'.join(new_lines)
        return None

    def extract_character_info_in_scenes(self):
        """
        Parses the transcript for scenes (denoted by the click of the tape
        recorder) and generates character info for each scene
        :return: None
        :rtype: None
        """
        for k, v in CHARACTER_CONSOLIDATION_DICT.items():
            self.transcript = self.transcript.replace(k, v)
        scene_list = re.split(
            r'\[TAPE CLICKS OFF.\][\n][\n][^\n][A-Za-z0-9 _.,!"\'\’\]]*|\[CLICK\]\n\n\[CLICK\]|\[TAPE CLICKS OFF\][\n][\n]\[TAPE CLICKS ON\]',
            self.transcript,
        )
        self.logger.debug(scene_list)
        for i, scene in enumerate(scene_list):
            self.character_info_in_scenes[i] = self.generate_character_info(
                scene
            )
        return None

    def generate_character_info(self, scene):
        """
        Parses a scene and, for each character in the scene, extracts the
        words spoken and their line appearances
        This assumes that:
         1. character names are formatted as a upper case word in its own line
         2. action sequences are formatted as a series of upper case words in
            square brackets
         3. dialogue is anything that isn't a character name or action sequence
        :param scene: Scene number
        :type scene: int
        :return: A nested dictionary where key is a character name and value is
            a dictionary with words spoken and line appearances
        :rtype: dict
        """
        lines = scene.split('\n')
        character_info = defaultdict(self.character_dict_default_value)
        current_character = ''
        counter = 0
        appearances = []
        for i, line in enumerate(lines):
            self.logger.debug(f'On line {i}: {line}')
            if re.match(
                '^[A-Z!]*$', line
            ):  # if it matches what looks like a character name
                self.logger.debug(
                    f'This is a character name. The current character is {current_character}'
                )
                if line == current_character:
                    self.logger.debug(f'This is the current character')
                    appearances.append(i)
                    self.logger.debug(appearances)
                    pass
                else:
                    self.logger.debug(
                        f'Time to change characters from {current_character} to {line}'
                    )
                    # check to see if it already is in the word count dictionary
                    if current_character in character_info:
                        self.logger.debug(
                            f'{current_character} is alredy in the dict.'
                        )
                        character_info[current_character][
                            'word_count'
                        ] += counter
                        character_info[current_character]['appearances'].extend(
                            appearances
                        )
                        self.logger.debug(f'Updated dict: {character_info}')
                    elif (
                        current_character
                    ):  # Don't add the placeholder empty string
                        self.logger.debug(
                            f'We need to add {current_character} to the dict'
                        )
                        character_info[current_character][
                            'word_count'
                        ] = counter
                        character_info[current_character][
                            'appearances'
                        ] = appearances
                        self.logger.debug(f'Updated dict: {character_info}')
                    current_character = line
                    counter = 0
                    appearances = [i]
            elif re.match(
                '\[[A-Za-z0-9 _.,!"\'\’]*\]', line
            ):  # check if this is an action
                self.logger.debug('This is an action sequence')
                pass
            else:
                counter += len(line.split())
            self.logger.debug(
                f'This is a line of dialogue. Updated counter for {current_character}: {counter}'
            )
        self.logger.debug(' ')
        return dict(character_info)

    @staticmethod
    def character_dict_default_value():
        """
        Creates default dictionary for character info in scene
        :return: default dictionary for character info in scene
        :rtype: dict
        """
        return {'word_count': 0, 'appearances': []}

    def generate_nodes_and_edges_dict(self):
        """
        Parses character info in each scene and generates a total nodes and
        edges dictionaries for the entire episode
        :return: None
        :rtype: None
        """
        for scene_i, scene_info in self.character_info_in_scenes.items():
            characters_in_scene = [c for c in scene_info]
            for character in characters_in_scene:
                self.update_individual_dict('node', character, scene_i)
            if len(characters_in_scene) == 2:
                cs = tuple(sorted(characters_in_scene))
                self.update_individual_dict('edge', cs, scene_i)
            elif len(characters_in_scene) > 2:
                cs_combo = [
                    i for i in itertools.combinations(characters_in_scene, 2)
                ]
                for p in cs_combo:
                    p = tuple(sorted(p))
                    self.update_individual_dict('edge', p, scene_i)
        self.logger.debug(f'Nodes: {pprint.pformat(self.nodes_dict)}')
        self.logger.debug(f'Edges: {pprint.pformat(self.edges_dict)}')
        return None

    def update_individual_dict(self, item_type, key, scene_i):
        """
        Checks for a key in a node/edge dictionary. Adds it with current scene
         attributes if it's not there. Updates its attributes if it is
        :param item_type: Either node or edge
        :type item_type: str
        :param key: Either a character name (for node) or tuple representing
            a character pair
        :type key: str or tuple
        :param scene_i: Scene number
        :type scene_i: int
        :return: None
        :rtype: None
        """
        assert item_type in ('node', 'edge')
        if item_type == 'node':
            item_dict = self.nodes_dict
            attribute = 'size'
            update = self.character_info_in_scenes[scene_i][key]['word_count']
        else:
            item_dict = self.edges_dict
            attribute = 'weight'
            update = self.get_edge_closeness_in_scene(scene_i, key[0], key[1])
        if key not in item_dict:
            item_dict[key] = {attribute: update}
        else:
            item_dict[key][attribute] += update
        return None

    def get_edge_closeness_in_scene(
        self,
        scene_i,
        character_1,
        character_2,
        lines_needed_for_interaction=LINES_NEEDED_FOR_CLOSENESS,
        min_closeness=MIN_CLOSENESS,
    ):
        """
        Calculates the closeness of a character pair in the scene
        The pair will start with a min_closeness score for just being in the
        same scene.
        Closeness increases by 2 every time the pair speak within min_lines
        of each other.
        :param scene_i: Scene number
        :type scene_i: int
        :param character_1: Name of a character in the pair
        :type character_1: str
        :param character_2: Name of another character in the pair
        :type character_2: str
        :param lines_needed_for_interaction: Threshold line number separation
            for increasing closeness score
        :type lines_needed_for_interaction: int
        :param min_closeness: Base closeness score for appearance in same scene
        :type min_closeness: float
        :return: Closeness score
        :rtype: float
        """
        list_1 = self.character_info_in_scenes[scene_i][character_1][
            'appearances'
        ]
        list_2 = self.character_info_in_scenes[scene_i][character_2][
            'appearances'
        ]
        l_idx, r_idx, counter, curr_count = 0, 0, 0, 0
        for num in list_1:
            while (
                l_idx < len(list_2)
                and num - list_2[l_idx] > lines_needed_for_interaction
            ):
                l_idx += 1
                curr_count -= 1
            while (
                r_idx < len(list_2)
                and list_2[r_idx] - num <= lines_needed_for_interaction
            ):
                r_idx += 1
                curr_count += 1
            counter += curr_count
        closeness = counter + min_closeness
        return closeness
