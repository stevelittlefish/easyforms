"""
This will test the connection before each query to see if the database has disconnected and recreate the connect.
Looks like magic to me...
"""

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

import logging

from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool

log = logging.getLogger(__name__)


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    # log.debug('Pinging postgresql server...')

    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except Exception as e:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        log.warn('Caught dodgy postgres disconnect: %s' % e)
        raise exc.DisconnectionError()
    cursor.close()
