"""
Functions for handling xml, normally using lxml
"""

import logging

from lxml import objectify, etree

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


def pretty_print_xml(xml, remove_blank_text=False):
    parser = etree.XMLParser(remove_blank_text=remove_blank_text)
    tree = etree.fromstring(xml, parser=parser)
    xml_output = etree.tostring(tree, pretty_print=True).decode()

    return xml_output
