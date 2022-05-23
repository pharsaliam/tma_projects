import itertools
import pprint
import pickle
import re
from collections import defaultdict

from utils import create_logger

CHARACTER_CONSOLIDATION_DICT = {
    '\nMAGNUS\n': '\nELIAS\n',
    '\nJOHN\n': '\nARCHIVIST\n'
}


class TMAEpisode:
    def __init__(self, episode_number, logging_level='INFO'):
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
        with open('episode_texts/tma_text_from_epub.pkl', 'rb') as f:
            all_episode_texts = pickle.load(f)
        html_text = all_episode_texts[self.number]
        tmarker1 = '[CLICK'
        tmarker2 = '[TAPE CLICKS'
        tmarker3 = 'End supplement'
        t_start_l = [html_text.find(tmarker1), html_text.find(tmarker2)]
        t_end_l = [html_text.rfind(tmarker1), html_text.rfind(tmarker2), html_text.find(tmarker3)]
        t_start_l = [i for i in t_start_l if i > 0]
        t_end_l = [i for i in t_end_l if i > 0]
        t_start = min(t_start_l + [0])
        t_end = max(t_end_l + [-1])
        self.transcript = html_text[t_start:t_end]

    def clean_up_character_names(self):
        lines = self.transcript.split('\n')
        new_lines = []
        for line in lines:
            if re.match('^[A-Z]* \([A-Z]*\)$', line):
                split = line.split()
                new_lines.append(split[0])
            else:
                new_lines.append(line)
        self.transcript = '\n'.join(new_lines)

    def extract_character_info_in_scenes(self):
        for k, v in CHARACTER_CONSOLIDATION_DICT.items():
            self.transcript = self.transcript.replace(k, v)
        scene_list = re.split(r'\[TAPE CLICKS OFF.\][\n][\n][^\n][A-Za-z0-9 _.,!"\'\’\]]*|\[CLICK\]\n\n\[CLICK\]|\[TAPE CLICKS OFF\][\n][\n]\[TAPE CLICKS ON\]', self.transcript)
        self.logger.debug(scene_list)
        for i, scene in enumerate(scene_list):
            self.character_info_in_scenes[i] = self.generate_character_info(
                scene)

    def generate_character_info(self, scene):
        lines = scene.split('\n')
        character_info = defaultdict(self.character_dict_default_value)
        current_character = ''
        counter = 0
        appearances = []
        for i, line in enumerate(lines):
            self.logger.debug(f'On line {i}: {line}')
            if re.match('^[A-Z]*$',
                        line):  # if it matches what looks like a character name
                self.logger.debug(
                    f'This is a character name. The current character is {current_character}')
                if line == current_character:
                    self.logger.debug(f'This is the current character')
                    appearances.append(i)
                    self.logger.debug(appearances)
                    pass
                else:
                    self.logger.debug(
                        f'Time to change characters from {current_character} to {line}')
                    # check to see if it already is in the word count dictionary
                    if (current_character in character_info):
                        self.logger.debug(
                            f'{current_character} is alredy in the dict.')
                        character_info[current_character][
                            'word_count'] += counter
                        character_info[current_character][
                            'appearances'].extend(appearances)
                        self.logger.debug(f'Updated dict: {character_info}')
                    elif current_character:  # Don't add the placeholder empty string
                        self.logger.debug(
                            f'We need to add {current_character} to the dict')
                        character_info[current_character][
                            'word_count'] = counter
                        character_info[current_character][
                            'appearances'] = appearances
                        self.logger.debug(f'Updated dict: {character_info}')
                    current_character = line
                    counter = 0
                    appearances = [i]
            elif re.match('\[[A-Za-z0-9 _.,!"\'\’]*\]',
                          line):  # check if this is an action
                self.logger.debug('This is an action sequence')
                pass
            else:
                counter += len(line.split())
            self.logger.debug(
                f'This is a line of dialogue. Updated counter for {current_character}: {counter}')
        self.logger.debug(' ')
        return dict(character_info)

    @staticmethod
    def character_dict_default_value():
        return {'word_count': 0, 'appearances': []}

    def generate_nodes_and_edges_dict(self):
        for scene_i, scene_info in self.character_info_in_scenes.items():
            characters_in_scene = [c for c in scene_info]
            for character in characters_in_scene:
                self.update_individual_node_dict(character, scene_i)
            if len(characters_in_scene) == 2:
                cs = tuple(sorted(characters_in_scene))
                self.update_individual_edge_dict(cs, scene_i)
            elif len(characters_in_scene) > 2:
                cs_combo = [i for i in itertools.combinations(characters_in_scene, 2)]
                for p in cs_combo:
                    p = tuple(sorted(p))
                    self.update_individual_edge_dict(p, scene_i)
        self.logger.debug(f'Nodes: {pprint.pformat(self.nodes_dict)}')
        self.logger.debug(f'Edges: {pprint.pformat(self.edges_dict)}')

    # TODO Consolidate this into a function
    def update_individual_node_dict(self, character, scene_i):
        if character not in self.nodes_dict:
            self.nodes_dict[character] = {'size': self.character_info_in_scenes[scene_i][character]['word_count']}
        else:
            self.nodes_dict[character]['size'] += self.character_info_in_scenes[scene_i][character]['word_count']

    def update_individual_edge_dict(self, pair, scene_i):
        if pair not in self.edges_dict:
            self.edges_dict[pair] = {'weight': self.get_edge_closeness_in_scene(scene_i, pair[0], pair[1])}
        else:
            self.edges_dict[pair]['weight'] += self.get_edge_closeness_in_scene(scene_i, pair[0], pair[1])

    def get_edge_closeness_in_scene(self, scene_i, character_1, character_2, min_lines=5, min_closeness=0.005):
        list_1 = self.character_info_in_scenes[scene_i][character_1]['appearances']
        list_2 = self.character_info_in_scenes[scene_i][character_2]['appearances']
        l_idx, r_idx, counter, curr_count = 0, 0, 0, 0
        for num in list_1:
            while l_idx < len(list_2) and num - list_2[l_idx] > min_lines:
                l_idx += 1
                curr_count -= 1
            while r_idx < len(list_2) and list_2[r_idx] - num <= min_lines:
                r_idx += 1
                curr_count += 1
            counter += curr_count
        closeness = (counter * 2) + min_closeness
        return closeness
