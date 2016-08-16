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
    'able', 'abundant', 'accepting', 'accommodating', 'active', 'addictive', 'adequate', 'aggressive', 'amazing', 'amiable', 'amicable', 'amusing', 'antagonistic', 'anxious', 'anxious', 'apathetic', 'aquatic', 'arrogant', 'articulate', 'artistic', 'attentive', 'attractive', 'authoritative', 'awesome',
    'barren', 'benevolent', 'biodegradable', 'blase', 'bold', 'bonding', 'boorish', 'bountiful', 'braggart', 'brave', 'brilliant', 'buoyancy', 'busy', 'buzz',
    'callow', 'captious', 'caring', 'celestial', 'charm', 'chaste', 'cheat', 'cheerful', 'churlish', 'civil', 'clean', 'clever', 'coastal', 'cold', 'colossal', 'combustible', 'comfortable', 'commercial', 'communicative', 'compact', 'competitive', 'compulsive', 'confident', 'conflicted', 'congenial', 'conscientious', 'conservative', 'considerate', 'conspicuous', 'contemptible', 'contiguous', 'cooperative', 'cordial', 'courageous', 'courteous', 'covetous', 'creative', 'critical', 'critical', 'crucial', 'crude', 'culpable', 'curious', 'current', 'curt', 'cynical',
    'decent', 'decorous', 'defensive', 'deferential', 'deft', 'dejected', 'delightful', 'demeaning', 'demise', 'dependable', 'deplorable', 'depressed', 'destructive', 'devious', 'devoted', 'dictatorial', 'diligent', 'diminutive', 'diplomatic', 'discreet', 'disdainful', 'dishonesty', 'dishonorable', 'disposable', 'disrespectful', 'distracted', 'docile', 'downcast', 'dynamic', 'dynamic',
    'earnest', 'earthy', 'ecological', 'efficient', 'egotistical', 'electrifying', 'elitist', 'empathetic', 'endangered', 'endemic', 'energetic', 'enigmatic', 'enthusiastic', 'esteemed', 'estimable', 'ethical', 'euphoric', 'evergreen', 'exclusive', 'expectant', 'explosive', 'exquisite', 'extravagant', 'extrovert', 'exuberant',
    'fair', 'faithful', 'fallow', 'falseness', 'famous', 'fancy', 'ferocious', 'fertile', 'fervent', 'fervid', 'fibrous', 'fierce', 'flexible', 'focused', 'forgiving', 'forlorn', 'frailty',
    'generous', 'genial', 'genteel', 'gentle', 'genuine', 'gifted', 'gigantic', 'glib', 'gloomy', 'good', 'gorgeous', 'grace', 'gracious', 'grand', 'grateful', 'gravity', 'green', 'grouchy', 'guilty', 'guilty', 'gusty',
    'happy', 'hard-hearted', 'healing', 'heedless', 'helpfulness', 'heroic', 'honest', 'honorable', 'hopeful', 'hostile', 'humane', 'humble', 'humorous', 'hygienic', 'hysterical',
    'idealistic', 'idolize', 'ignoble', 'ignorant', 'ill-tempered', 'impartial', 'impolite', 'improper', 'imprudent', 'impudent', 'indecent', 'indecorous', 'indifference', 'indigenous', 'industrious', 'ingenuous', 'innocent', 'innovative', 'insightful', 'insolent', 'inspirational', 'instructive', 'insulting', 'intense', 'intense', 'intense', 'intolerant', 'introvert', 'intuitive', 'inventive', 'investigative', 'irascible', 'irresponsible',
    'jaundiced', 'jealous', 'jealous', 'jocular', 'jolly', 'jovial', 'joyful', 'jubilant', 'just', 'juvenile',
    'keen', 'kind', 'kindred', 'knowledgeable',
    'liberal', 'listener', 'loathsome', 'loving', 'loyal',
    'magical', 'magnificence', 'magnificent', 'malevolent', 'malicious', 'mammoth', 'manipulative', 'marine', 'mastery', 'meddling', 'meritorious', 'meticulous', 'migratory', 'minuscule', 'miserable', 'mistrustful', 'modest', 'moral', 'mysterious',
    'naive', 'nascent', 'native', 'natural', 'natural', 'nature', 'needy', 'nefarious', 'negative', 'neglected', 'neglectful', 'negligent', 'nice', 'noble', 'notorious',
    'obedient', 'observant', 'open', 'open-minded', 'opinionated', 'oppressive', 'orderly', 'oriented', 'original', 'outrageous', 'outspoken',
    'parasitic', 'partial', 'passionate', 'patient', 'perceptive', 'personable', 'personal', 'petulant', 'pleasant', 'poise', 'polite', 'pollutant', 'popular', 'popular', 'powerful', 'prejudicial', 'preposterous', 'pretentious', 'prideful', 'principled', 'pristine', 'prompt', 'proper', 'punctual', 'purposeful',
    'quaint', 'quarrelsome', 'quick', 'quiet', 'quiet', 'quirky',
    'radioactive', 'rancorous', 'rational', 'reasonable', 'reckless', 'refined', 'reflective', 'reliant', 'remarkable', 'remorseful', 'renewable', 'reproductive', 'repugnant', 'resilient', 'resilient', 'resolute', 'resourceful', 'respectful', 'responsible', 'responsive', 'restorative', 'reverent', 'rotting', 'rude', 'ruthless',
    'sadness', 'safe', 'scornful', 'scrumptious', 'selfish', 'sensible', 'sensitive', 'sharing', 'simple', 'sober', 'solar', 'solemn', 'solitary', 'soluble', 'sour', 'spatial', 'special', 'splendid', 'splendid', 'staunch', 'staunch', 'stern', 'stunning', 'successful', 'sullen', 'superb', 'superior', 'supportive', 'surly', 'suspicious', 'sweet', 'sympathetic',
    'tactful', 'tainted', 'temperate', 'temperate', 'tenacious', 'terrific', 'testy', 'thoughtful', 'thoughtless', 'tolerant', 'towering', 'toxic', 'treacherous', 'tropical', 'trustworthy', 'truthful',
    'ultimate', 'ultimate', 'uncivil', 'uncouth', 'undeveloped', 'unethical', 'unfair', 'unique', 'unique', 'united', 'unity', 'unmannerly', 'unrefined', 'unsavory', 'unworthy', 'uplifting', 'upright', 'uproot', 'upstanding',
    'valiant', 'veracious', 'versatile', 'vicious', 'vigilant', 'vigilant', 'vigorous', 'vile', 'villainous', 'virtuous', 'visible', 'visible', 'vivacious', 'vocal', 'volatile', 'volunteering', 'vulnerable',
    'warm', 'wary', 'waspish', 'watchful', 'welcoming', 'wicked', 'wild', 'willingness', 'winning', 'winsome', 'wise', 'wishy-washy', 'wistful', 'witty', 'woeful', 'wonderful', 'worldwide', 'worrier', 'worthwhile', 'worthy',
    'yearning', 'yielding', 'yielding', 'yourself', 'youthful',
    'zany', 'zealot', 'zealous', 'zealous', 'zero-tolerant'
]
NOUNS = [
    'cheese', 'passenger', 'judge', 'bait', 'bell', 'shelf', 'instrument', 'grandfather',
    'impulse', 'thunder', 'ear', 'control', 'seashore', 'fall', 'meeting', 'wish',
    'sock', 'sleep', 'celery', 'suggestion', 'cup', 'office', 'boat', 'stamp',
    'middle', 'ticket', 'theory', 'loss', 'finger', 'finger', 'head', 'flower',
    'turkey', 'pies', 'gun', 'governor', 'side', 'dog', 'number', 'pump',
    'holiday', 'sand', 'start', 'burst', 'eye', 'harmony', 'temper', 'leg',
    'increase', 'measure', 'queen', 'bone', 'taste', 'oatmeal', 'cart', 'wire',
    'expert', 'rail', 'sink', 'rice', 'locket', 'scissors', 'toes', 'plot',
    'snails', 'car', 'crow', 'nut', 'snake', 'ladybug', 'birthday', 'birds',
    'cows', 'person', 'drain', 'knee', 'plate', 'hair', 'jelly', 'ducks',
    'toothbrush', 'calculator', 'receipt', 'noise', 'wax', 'company', 'stone', 'woman',
    'humor', 'position', 'wool', 'angle', 'town', 'riddle', 'alarm', 'yak',
    'agreement', 'roof', 'fork', 'rhythm', 'basket', 'war', 'cannon', 'glass',
    'lunchroom', 'van', 'ground', 'spot', 'playground', 'camera', 'jump', 'balance',
    'bit', 'orange', 'scene', 'powder', 'quince', 'water', 'yarn', 'sound',
    'breath', 'library', 'play', 'carriage', 'drop', 'magic', 'wave', 'servant',
    'cobweb', 'vein', 'flesh', 'quiver', 'rule', 'giants', 'railway', 'observation',
    'bat', 'wall', 'toothpaste', 'death', 'brick', 'picture', 'move', 'secretary',
    'kitty', 'smash', 'adjustment', 'carpenter', 'hate', 'yard', 'grip', 'sheet',
    'exchange', 'pot', 'bomb', 'guide', 'space', 'fowl', 'yoke', 'needle',
    'mine', 'discussion', 'wealth', 'cherries', 'addition', 'star', 'morning', 'color',
    'monkey', 'books', 'airport', 'power', 'dogs', 'afternoon', 'butter', 'toys',
    'elbow', 'cherry', 'bath', 'quill', 'road', 'copper', 'arch', 'rabbit',
    'lumber', 'thing', 'cent', 'show', 'care', 'dress', 'horse', 'spring',
    'page', 'sail', 'babies', 'hammer', 'night', 'aftermath', 'reason', 'memory',
    'class', 'mother', 'business', 'interest', 'food', 'rat', 'grain', 'quiet',
    'brother', 'industry', 'sheep', 'wound', 'glove', 'stocking', 'digestion', 'chance',
    'duck', 'run', 'tooth', 'truck', 'territory', 'skate', 'fish', 'room',
    'mind', 'top', 'pleasure', 'pickle', 'underwear', 'rifle', 'honey', 'rate',
    'transport', 'brass', 'bike', 'voice', 'smile', 'lake', 'toad', 'kettle',
    'street', 'wrist', 'market', 'desk', 'request', 'chicken', 'sky', 'wren',
    'part', 'sweater'
]
QUALIFIERS = [
    'rather', 'quite', 'very', 'exceedingly', 'pretty', 'almost', 'not quite',
    'absolutely', 'mostly', 'almost', 'most definitely'
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

    def generate_adjective_noun(self, qualifier_chance=0.3, the_chance=0.1, adjective_chance=0.95):
        parts = []
        if random.random() < the_chance:
            parts.append('the')
        if random.random() < adjective_chance:
            if random.random() < qualifier_chance:
                parts.append(random.choice(self.qualifiers))
            parts.append(random.choice(self.adjectives))
        parts.append(random.choice(self.nouns))

        return ' '.join(parts)

