"""
Exceptions for forms library
"""

import logging

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


class FieldNotFound(Exception):
    pass


class AlreadyProcessed(Exception):
    pass


class FormNotProcessed(Exception):
    pass


class DuplicateField(Exception):
    pass

