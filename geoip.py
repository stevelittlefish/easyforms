"""
For doing geo ip lookups
"""

import logging

import geoip2.database

__author__ = 'Yu Lee Paul (Little Fish Solutions LTD)'


log = logging.getLogger(__name__)

_reader = None


def init(geolite2_path):
    global _reader
    log.info('Loading geoip data from %s' % geolite2_path)
    _reader = geoip2.database.Reader(geolite2_path)


def get_geoip_data(ip):
    return _reader.city(ip)
