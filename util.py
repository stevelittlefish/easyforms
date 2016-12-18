"""
Utility Functions
"""

import logging
import os
from io import StringIO
import csv
from functools import wraps
import random
import re

from flask import jsonify, make_response
import flask
import jinja2

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)

LOWER_CASE = 'abcdefghijkmnopqrstuvwxyz'
UPPER_CASE = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'
NUMBERS = '0123456789'
SYMBOLS = '!?@%'

BASE62_MAP = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

paragraph_split_regex = re.compile(r'\n\n+')


def generate_password():
    return random.choice(UPPER_CASE)\
        + random.choice(LOWER_CASE)\
        + random.choice(LOWER_CASE)\
        + random.choice(LOWER_CASE)\
        + random.choice(LOWER_CASE)\
        + random.choice(NUMBERS)\
        + random.choice(NUMBERS)\
        + random.choice(SYMBOLS)


def ajax_error(error_message):
    return jsonify({'status': 'error', 'message': error_message})


def format_number_1dp(number):
    if number is None:
        return None
    return ("%.1f" % number).rstrip('0').rstrip('.')


def format_number_2dp(number):
    if number is None:
        return None
    return ("%.2f" % number).rstrip('0').rstrip('.')


def format_number_2dp_trailing_zeros(number):
    if number is None:
        return None
    return "%.2f" % number


def format_price(price):
    if price is None:
        return None
    return jinja2.Markup('&pound;%0.2f' % price)


def format_price_commas_no_point(price):
    """
    Formats prices, rounding (i.e. to the nearest whole number of pounds) with commas

    Why is this in the library?
    """
    if price is None:
        return None
    return jinja2.Markup('&pound;{:,.0f}'.format(price))


def format_commas(number):
    """
    Rounds a number and formats it with commas i.e. 123,456,789
    """
    if number is None:
        return None
    return '{:,.0f}'.format(number)


def format_multiline_html(text):
    """
    Turns a string like 'a\nb\nc' into 'a<br>b<br>c' and marks as Markup

    Note: Will remove all \r characters from output (if present)
    """
    if text is None:
        return None

    if '\n' not in text:
        return text.replace('\r', '')

    parts = text.replace('\r', '').split('\n')
    out = flask.Markup()
    for part in parts:
        if out:
            out += flask.Markup('<br>')
        out += flask.escape(part)
    return out


def to_paragraphs(string):
    # Split the string into parts using multiple returns as a separator
    parts = paragraph_split_regex.split(string)
    return flask.Markup('<p>%s</p>' % '</p><p>'.join(parts))


def format_filesize(bytes):
    one_mb = 1024 * 1024

    if bytes < 1024:
        return '%s Bytes' % bytes
    elif bytes < one_mb:
        return '%0.1f KiB' % (float(bytes) / 1024)
    else:
        return '%0.1f MiB' % (float(bytes) / one_mb)


def format_ordinal(n):
    """
    Format an ordinal, like 1st, 2nd, 3rd...

    Not tested with large numbers of negative numbers!
    """
    if 10 <= n % 100 < 20:
        return str(n) + 'th'
    else:
        return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, "th")


def is_ascii(s):
    """
    Check if a "bytes" contains all ascii characters
    :param s: the string to check
    :return: true if the string is entirely ascii characters
    """
    try:
        s.decode('ascii')
    except UnicodeDecodeError:
        return False
    return True


def ensure_dir(path):
    """Ensure that a needed directory exists, creating it if it doesn't"""
    try:
        log.info('Ensuring directory exists: %s' % path)
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


def extension_from_filename(filename):
    return filename.rsplit('.')[-1]


def make_csv_response(csv_data, filename):
    """
    :param csv_data: A string with the contents of a csv file in it
    :param filename: The filename that the file will be saved as when it is downloaded by the user
    :return: The response to return to the web connection
    """
    resp = make_response(csv_data)
    resp.headers['Content-Type'] = 'application/octet-stream'
    resp.headers['Content-Disposition'] = 'attachment; filename=%s' % filename

    return resp


def rows_to_csv(rows, filename='report.csv', header=None):
    outfile = StringIO()
    writer = csv.writer(outfile)
    if header:
        writer.writerow(header)
    for row in rows:
        try:
            writer.writerow(row)
        except UnicodeEncodeError:
            replacement_row = []
            for item in row:
                # if item contains utf-8 characters, then replace string with 'INVALID'
                if not isinstance(item, str) or is_ascii(item):
                    replacement_row.append(item)
                else:
                    replacement_row.append('!!INVALID!!')
            writer.writerow(replacement_row)

    return make_csv_response(outfile.getvalue(), filename)


def no_cache(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        h = resp.headers
        h['Cache-Control'] = 'private, no-store, max-age=0, no-cache, must-revalidate, post-check=0, pre-check=0'
        h['Pragma'] = 'no-cache'
        h['Expires'] = 'Fri, 01 Jan 1990 00:00:00 GMT'
        return resp

    return decorated


def to_base62(n):
    """
    Converts a number to base 62
    :param n: The number to convert
    :return: Base 62 representation of number (string)
    """
    remainder = n % 62
    result = BASE62_MAP[remainder]
    num = n / 62

    while num > 0:
        remainder = num % 62
        result = '%s%s' % (BASE62_MAP[remainder], result)
        num = num / 62

    return result


def from_base62(s):
    """
    Convert a base62 String back into a number
    :param s: The base62 encoded String
    :return: The number encoded in the String (integer)
    """
    result = 0

    for c in s:
        if c not in BASE62_MAP:
            raise Exception('Invalid base64 string: %s' % s)

        result = result * 62 + BASE62_MAP.index(c)

    return result


def read_file(filename):
    with open(filename, 'rb') as f:
        file_data = f.read()
        return file_data


def write_file(filename, data):
    with open(filename, 'wb') as f:
        f.write(data)


def chunks(l, n):
    """Yield successive n-sized chunks from list"""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def generate_random_numeric_string(length):
    return ''.join(random.choice(NUMBERS) for x in range(length))

