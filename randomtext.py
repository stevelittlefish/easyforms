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

ADJECTIVES = [
    'able', 'abundant', 'accepting', 'accommodating', 'active', 'addictive', 'adequate',
    'aggressive', 'amazing', 'ambiguousbarren', 'amiable', 'amicable', 'amusing',
    'antagonistic', 'anxious', 'apathetic', 'aquatic', 'arrogant', 'articulate',
    'artistic', 'attentive', 'attractive', 'authoritative', 'awesome',
    
    'benevolent', 'biodegradable', 'blase', 'bold', 'bonding', 'boorish', 'bountiful',
    'braggart', 'brave', 'brilliant', 'buoyant', 'busy', 'buzzing',
    
    'callow', 'captious', 'caring', 'celestial', 'charming', 'chaste', 'cheating',
    'cheerful', 'churlish', 'civil', 'clean', 'clever', 'coastal', 'cold', 'colossal',
    'combustible', 'comfortable', 'commercial', 'communicative', 'compact',
    'competitive', 'compulsive', 'confident', 'conflicted', 'congenial', 'conscientious',
    'conservative', 'considerate', 'conspicuous', 'contemptible', 'contiguous',
    'cooperative', 'cordial', 'courageous', 'courteous', 'covetous', 'creative',
    'critical', 'critical', 'crucial', 'crude', 'culpable', 'curious', 'current', 'curt',
    'cynical', 'cool',
    
    'decent', 'decorous', 'defensive', 'deferential', 'deft', 'dejected', 'delightful',
    'demeaning', 'demise', 'dependable', 'deplorable', 'depressed', 'destructive',
    'devious', 'devoted', 'dictatorial', 'diligent', 'diminutive', 'diplomatic',
    'discreet', 'disdainful', 'dishonest', 'dishonorable', 'disposable', 'disrespectful',
    'distracted', 'docile', 'downcast', 'dynamic',
    
    'earnest', 'earthy', 'ecological', 'efficient', 'egotistical', 'electrifying', 'elitist',
    'empathetic', 'endangered', 'endemic', 'energetic', 'enigmatic', 'enthusiastic',
    'esteemed', 'estimable', 'ethical', 'euphoric', 'evergreen', 'exclusive',
    'expectant', 'explosive', 'exquisite', 'extravagant', 'extrovert', 'exuberant',
    
    'fair', 'faithful', 'fallow', 'false', 'famous', 'fancy', 'ferocious', 'fertile',
    'fervent', 'fervid', 'fibrous', 'fierce', 'flexible', 'focused', 'forgiving',
    'forlorn', 'frail', 'foolish',
    
    'generous', 'genial', 'genteel', 'gentle', 'genuine', 'gifted', 'gigantic', 'glib',
    'gloomy', 'good', 'gorgeous', 'grace', 'gracious', 'grand', 'grateful',
    'green', 'grouchy', 'guilty', 'guilty', 'gusty',
    
    'happy', 'hard-hearted', 'healing', 'heedless', 'helpful', 'heroic', 'honest',
    'honorable', 'hopeful', 'hostile', 'humane', 'humble', 'humorous', 'hygienic',
    'hysterical',
    
    'idealistic', 'idolize', 'ignoble', 'ignorant', 'ill-tempered', 'impartial', 'impolite',
    'improper', 'imprudent', 'impudent', 'indecent', 'indecorous', 'indifferent',
    'indigenous', 'industrious', 'ingenuous', 'innocent', 'innovative', 'insightful',
    'insolent', 'inspirational', 'instructive', 'insulting', 'intense', 'intense',
    'intense', 'intolerant', 'introvert', 'intuitive', 'inventive', 'investigative',
    'irascible', 'irresponsible',
    
    'jaundiced', 'jealous', 'jealous', 'jocular', 'jolly', 'jovial', 'joyful', 'jubilant',
    'just', 'juvenile',
    
    'keen', 'kind', 'kindred', 'knowledgeable',
    
    'liberal', 'listener', 'loathsome', 'loving', 'loyal',
    
    'magical', 'magnificent', 'malevolent', 'malicious', 'mammoth',
    'manipulative', 'marine', 'mastery', 'meddling', 'meritorious', 'meticulous',
    'migratory', 'minuscule', 'miserable', 'mistrustful', 'modest', 'moral',
    'mysterious',
    
    'naive', 'nascent', 'native', 'natural', 'natural', 'needy', 'nefarious', 'negative',
    'neglected', 'neglectful', 'negligent', 'nice', 'noble', 'notorious', 'nonsensical',
    
    'obedient', 'observant', 'open', 'open-minded', 'opinionated', 'oppressive', 'orderly',
    'oriented', 'original', 'outrageous', 'outspoken', 'over-the-top',
    
    'parasitic', 'partial', 'passionate', 'patient', 'perceptive', 'personable', 'personal',
    'petulant', 'pleasant', 'poise', 'polite', 'pollutant', 'popular', 'popular',
    'powerful', 'prejudicial', 'preposterous', 'pretentious', 'prideful', 'principled',
    'pristine', 'prompt', 'proper', 'punctual', 'purposeful',
    
    'quaint', 'quarrelsome', 'quick', 'quiet', 'quirky',
    
    'radioactive', 'rancorous', 'rational', 'reasonable', 'reckless', 'refined',
    'reflective', 'reliant', 'remarkable', 'remorseful', 'renewable', 'reproductive',
    'repugnant', 'resilient', 'resilient', 'resolute', 'resourceful', 'respectful',
    'responsible', 'responsive', 'restorative', 'reverent', 'rotting', 'rude',
    'ruthless', 'religious',
    
    'sadness', 'safe', 'scornful', 'scrumptious', 'selfish', 'sensible', 'sensitive',
    'sharing', 'simple', 'sober', 'solar', 'solemn', 'solitary', 'soluble', 'sour',
    'spatial', 'special', 'splendid', 'splendid', 'staunch', 'staunch', 'stern',
    'stunning', 'successful', 'sullen', 'superb', 'superior', 'supportive', 'surly',
    'suspicious', 'sweet', 'sympathetic', 'single',
    
    'tactful', 'tainted', 'temperate', 'temperate', 'tenacious', 'terrific', 'testy',
    'thoughtful', 'thoughtless', 'tolerant', 'towering', 'toxic', 'treacherous',
    'tropical', 'trustworthy', 'truthful',
    
    'ultimate', 'ultimate', 'uncivil', 'uncouth', 'undeveloped', 'unethical', 'unfair',
    'unique', 'unique', 'united', 'unity', 'unmannerly', 'unrefined', 'unsavory',
    'unworthy', 'uplifting', 'upright', 'uprooted', 'upstanding',
    
    'valiant', 'veracious', 'versatile', 'vicious', 'vigilant', 'vigorous', 'vile',
    'villainous', 'virtuous', 'visible', 'vivacious', 'vocal', 'volatile',
    'volunteering', 'vulnerable',
    
    'warm', 'wary', 'waspish', 'watchful', 'welcoming', 'wicked', 'wild', 'willingness',
    'winning', 'winsome', 'wise', 'wishy-washy', 'wistful', 'witty', 'woeful',
    'wonderful', 'worldwide', 'worrier', 'worthwhile', 'worthy',
    
    'yearning', 'yielding', 'youthful',
    
    'zany', 'zealous', 'zero-tolerant'
]

NOUNS = [
    'addition', 'adjustment', 'aftermath', 'afternoon', 'agreement', 'airport', 'alarm',
    'albino', 'ambiguity', 'angle', 'arch', 'astonishment',
    
    'babies', 'bait', 'balance', 'ball-bearing', 'basket', 'bat', 'bath', 'bell', 'bike',
    'birds', 'birthday', 'bit', 'boat', 'bomb', 'bone', 'books', 'brass', 'breath',
    'brick', 'brother', 'burst', 'business', 'butter',
    
    'calculator', 'camera', 'cannon', 'car', 'care', 'carpenter', 'carriage', 'cart',
    'celery', 'cent', 'chance', 'cheese', 'cherries', 'cherry', 'chicken', 'class',
    'cobweb', 'color', 'company', 'connection', 'control', 'copper', 'cows', 'crow',
    'cup', 'corncob',
    
    'danger', 'death', 'desk', 'digestion', 'discussion', 'dog', 'dogs', 'drain', 'dress',
    'drop', 'duck', 'ducks',
    
    'ear', 'elbow', 'elephant', 'empathy', 'exchange', 'expert', 'explosion', 'eye',
    
    'face', 'fall', 'finger', 'finger', 'fish', 'flesh', 'flower', 'food', 'fork', 'fowl',
    'fractal',
    
    'giants', 'gin', 'girl', 'glass', 'glove', 'governor', 'grain', 'grandfather', 'grin', 'grip',
    'ground', 'guide', 'gun', 'gravity',
    
    'hair', 'hammer', 'harmony', 'hate', 'head', 'hilarity', 'holiday', 'honey', 'horse',
    'humor',
    
    'impulse', 'incompetence', 'increase', 'increase', 'industry', 'instrument', 'interest',
    
    'jelly', 'jelly bean', 'judge', 'jump', 'jungle',
    
    'kelp', 'kettle', 'kitty', 'knee',
    
    'lady', 'ladybug', 'lake', 'leg', 'library', 'locket', 'loss', 'lumber', 'lunchroom',
    
    'magic', 'man', 'market', 'measure', 'meatloaf', 'meeting', 'memory', 'middle', 'mind', 'mine',
    'monkey', 'monster', 'morning', 'mother', 'move',
    
    'needle', 'newt', 'night', 'noise', 'nothing', 'number', 'nut',
    
    'oatmeal', 'observation', 'offal', 'office', 'orange',
    
    'page', 'part', 'passenger', 'person', 'pickle', 'picture', 'pies', 'plate', 'play',
    'playground', 'pleasure', 'plot', 'position', 'pot', 'powder', 'power', 'proton',
    'pump',
    
    'queen', 'quiet', 'quill', 'quince', 'quiver',
    
    'rabbit', 'rail', 'railway', 'rat', 'rate', 'reality', 'reason', 'receipt',
    'request', 'rhythm', 'rice', 'riddle', 'ridicule', 'rifle', 'road', 'roof', 'room', 'rule',
    'run',
    
    'sand', 'sandwich', 'sail', 'scene', 'scissors', 'seashore', 'secretary', 'servant', 'sheep',
    'sheet', 'shelf', 'show', 'side', 'sink', 'skate', 'sky', 'sleep', 'smash', 'smile',
    'snails', 'snake', 'sock', 'sound', 'space', 'spot', 'spring', 'stamp', 'star',
    'start', 'stocking', 'stone', 'street', 'suggestion', 'sweater',
    
    'taste', 'temper', 'territory', 'theory', 'thing', 'thunder', 'ticket', 'toad', 'toes',
    'tooth', 'toothbrush', 'toothpaste', 'top', 'town', 'toys', 'transport', 'truck',
    'turkey', 'turnip', 'tyrant',
    
    'underwear', 'utopia',
    
    'van', 'vein', 'vernacular', 'voice',
    
    'wall', 'war', 'water', 'wave', 'wax', 'wealth', 'wire', 'wish', 'wind', 'woman', 'wool',
    'wound', 'wren', 'wrist',
    
    'xylophone',
    
    'yak', 'yard', 'yarn', 'yoke',
    
    'zen'
]

QUALIFIERS = [
    'rather', 'quite', 'very', 'exceedingly', 'pretty', 'almost', 'not quite',
    'absolutely', 'mostly', 'almost', 'most definitely', 'disturbingly', 'ridiculously',
    'spectacularly', 'slightly', 'nearly', 'annoyingly', 'ambiguously', 'possibly',
    'disproportionately', 'seemingly'
]


class TextGenerator(object):
    def __init__(self, filename, escape_quotes=False):
        """
        :param filename: Path to a markov chain data file (generated using markov_tool)
        """
        self.markov = pymarkovchain.MarkovChain(filename)
        self.escape_quotes = escape_quotes
        self.nouns = NOUNS
        self.adjectives = ADJECTIVES
        self.qualifiers = QUALIFIERS
    
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

    def generate_sentence(self, min=None, max=None, punctuation=True):
        end = random.choice(PUNCTUATION) if punctuation else ''
        return self.generate_text(min=min, max=max) + end

    def generate_sentences(self, min_sentences=1, max_sentences=6, min_sentence_length=30, max_sentence_length=200):
        sentences = []
        num_sentences = random.randint(min_sentences, max_sentences)
        for i in range(num_sentences):
            sentences.append(self.generate_sentence(min=min_sentence_length, max=max_sentence_length))

        return ' '.join(sentences)

    def generate_html_paragraph(self, min_sentences=1, max_sentences=6, min_sentence_length=30, max_sentence_length=200):
        return '<p>{}</p>'.format(self.generate_sentences(min_sentences, max_sentences,
                                                          min_sentence_length,
                                                          max_sentence_length))
   
    def generate_html_paragraphs(self, min_paragraphs=2, max_paragraphs=5, min_sentences=1, max_sentences=7, min_sentence_length=10, max_sentence_length=130):
        paragraphs = []
        num_paragraphs = random.randint(min_paragraphs, max_paragraphs)
        for i in range(num_paragraphs):
            paragraphs.append(self.generate_html_paragraph(min_sentences, max_sentences,
                                                           min_sentence_length, max_sentence_length))

        return '\n'.join(paragraphs)

    def generate_html_list(self, min_items=3, max_items=7, min_item_length=20, max_item_length=100):
        ul = '<ul>'
        num_list_items = random.randint(min_items, max_items)
        for i in range(num_list_items):
            ul += '<li>{}</li>'.format(self.generate_text(min=min_item_length, max=max_item_length))
        ul += '</ul>'

        return ul

    def generate_adjective_noun(self, qualifier_chance=0.3, the_chance=0.1, adjective_chance=0.9, the_double_noun_chance=0.08):
        if random.random() < the_double_noun_chance:
            return 'the {} {}'.format(random.choice(self.nouns), random.choice(self.nouns))

        parts = []
        if random.random() < the_chance:
            parts.append('the')
        if random.random() < adjective_chance:
            if random.random() < qualifier_chance:
                parts.append(random.choice(self.qualifiers))
            parts.append(random.choice(self.adjectives))
        parts.append(random.choice(self.nouns))

        return ' '.join(parts)

