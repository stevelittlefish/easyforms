"""
Contains code for generating random placeholder text
"""

import logging
import random

import pymarkovchain

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)

MAX_ATTEMPTS = 30
PUNCTUATION = '...........?!!'


class TextGenerator(object):
    def __init__(self, filename, escape_quotes=False):
        """
        :param filename: Path to a markov chain data file (generated using markov_tool)
        """
        self.markov = pymarkovchain.MarkovChain(filename)
        self.escape_quotes = escape_quotes
    
    def _process_text(self, text):
        if self.escape_quotes:
            text = text.replace('"', '&quot;')
        return text

    def generate_text(self, min=None, max=None):
        for i in range(MAX_ATTEMPTS):
            result = self.markov.generateString()
            l = len(result)
            if min and l < min:
                continue
            if max and l > max:
                continue

            return self._process_text(result)
        
        # We couldn't get one of the right length
        if max > 5:
            result = result[:max - 3] + '...'
        
        return self._process_text(result)

    def generate_sentence(self, min=None, max=None):
        return self.generate_text(min=min, max=max) + random.choice(PUNCTUATION)

    def generate_html_paragraph(self, min_sentences=1, max_sentences=7, min_sentence_length=10, max_sentence_length=130):
        paragraph = '<p>'
        num_sentences = random.randint(min_sentences, max_sentences)
        for i in range(num_sentences):
            paragraph += self.generate_sentence(min=min_sentence_length, max=max_sentence_length) + ' '
        paragraph += '</p>'

        return paragraph
    
    def generate_html_list(self, min_items=3, max_items=7, min_item_length=20, max_item_length=100):
        ul = '<ul>'
        num_list_items = random.randint(min_items, max_items)
        for i in range(num_list_items):
            ul += '<li>{}</li>'.format(self.generate_text(min=min_item_length, max=max_item_length))
        ul += '</ul>'

        return ul
