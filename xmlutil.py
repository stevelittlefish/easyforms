"""
Functions for handling xml, normally using lxml
"""

import logging

from lxml import objectify

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


def remove_namespaces(root):
    """Call this on an lxml.etree document to remove all namespaces"""
    for elem in root.getiterator():
        if not hasattr(elem.tag, 'find'):
            continue

        i = elem.tag.find('}')
        if i >= 0:
            elem.tag = elem.tag[i + 1:]

    objectify.deannotate(root, cleanup_namespaces=True)

