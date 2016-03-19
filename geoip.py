"""
For doing geo ip lookups
"""

__author__ = 'Yu Lee Paul (Little Fish Solutions LTD)'

import logging

import geoip2.database

from app import app

log = logging.getLogger(__name__)

_geolite2_path = app.config['GEOLITE2_PATH']
log.info('Loading geoip data from %s' % _geolite2_path)
_reader = geoip2.database.Reader(_geolite2_path)


def get_geoip_data(ip):
    return _reader.city(ip)
