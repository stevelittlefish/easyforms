"""
Utility functions for processing HTML
"""

import logging
import re

from bs4 import BeautifulSoup

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)

INLINE_TAGS = ['a', 'span', 'em', 'strong', 'b', 'big', 'i', 'small', 'tt', 'abbr', 'acronym',
               'cite', 'code', 'em', 'img', 'sub', 'sup']


def get_all_text(html):
    soup = BeautifulSoup(html, "lxml")
    return soup.find_all(text=True)


def split_line(line, min_line_length=30, max_line_length=100):
    """
    This is designed to work with prettified output from Beautiful Soup which indents with a single space.

    :param line: The line to split
    :param min_line_length: The minimum desired line length
    :param max_line_length: The maximum desired line length

    :return: A list of lines
    """
    if len(line) <= max_line_length:
        # No need to split!
        return [line]

    # First work out the indentation on the beginning of the line
    indent = 0
    while line[indent] == ' ' and indent < len(line):
        indent += 1

    # Try to split the line
    # Start looking for a space at character max_line_length working backwards
    i = max_line_length
    split_point = None
    while i > min_line_length:
        if line[i] == ' ':
            split_point = i
            break
        i -= 1

    if split_point is None:
        # We didn't find a split point - search beyond the end of the line
        i = max_line_length + 1
        while i < len(line):
            if line[i] == ' ':
                split_point = i
                break
            i += 1

    if split_point is None:
        # There is nowhere to split the line!
        return [line]
    else:
        # Split it!
        line1 = line[:split_point]
        line2 = ' ' * indent + line[split_point + 1:]
        return [line1] + split_line(line2, min_line_length, max_line_length)


def pretty_print(html, max_line_length=110, tab_width=4):
    """
    Pretty print HTML, splitting it into lines of a reasonable length (if possible).

    This probably needs a whole lot more testing!

    :param html: The HTML to format
    :param max_line_length: The desired maximum line length. Will not be strictly adhered to
    :param min_line_length: The desired minimum line length
    :param tab_width: Essentially, the tabs that indent the code will be treated as this many
                      spaces when counting the length of each line

    :return: Beautifully formatted HTML
    """
    if tab_width < 2:
        raise ValueError('tab_width must be at least 2 (or bad things would happen!)')

    # Double curly brackets to avoid problems with .format()
    html = html.replace('{', '{{').replace('}', '}}')
    soup = BeautifulSoup(html, 'lxml')
    soup.html.unwrap()
    soup.body.unwrap()

    unformatted_tag_list = []
    
    # Here we are taking the tags out of the content and replacing them with placeholders,
    # and adding the tags to a list.  I didn't come up with this...
    for i, tag in enumerate(soup.find_all(INLINE_TAGS)):
        unformatted_tag_list.append(str(tag))
        tag.replace_with('{' + 'unformatted_tag_list[{0}]'.format(i) + '}')

    # If we prettify this, there will still be some weird indentation going on, based on
    # the original markup, so we need to convert it into a string again, and then parse
    # it again
    processed_html = str(soup)
    soup2 = BeautifulSoup(processed_html, 'lxml')
    soup2.html.unwrap()
    soup2.body.unwrap()

    # Prettify it, substitute in the unformatted tags
    pretty_markup = soup2.prettify().format(unformatted_tag_list=unformatted_tag_list)

    # Convert indendtations to a tab width of 4
    pretty_markup = re.sub(r'^(\s+)', r'\1' * tab_width, pretty_markup, flags=re.MULTILINE)

    # Final step - pass over the formatted html, convert the indentations into tabs and cut
    # the lines to length
    lines = pretty_markup.splitlines()
    out = ''
    for line in lines:
        for line_part in split_line(line, max_line_length=max_line_length):
            out += line_part
            out += '\n'
    
    # Final final step! Convert space indentations into tabs
    return out.replace(' ' * tab_width, '\t')
