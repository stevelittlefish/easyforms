"""
Code to manage session variables
"""

import logging

from flask import session

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)

KEY_BS_VERSION = 'bs-version'


def get_bs_version():
    # Default to 4
    return session.get(KEY_BS_VERSION, 4)


def set_bs_version(version):
    if version not in [3, 4]:
        raise ValueError('Invalid Bootstrap Version: {}'.format(version))

    session[KEY_BS_VERSION] = version

