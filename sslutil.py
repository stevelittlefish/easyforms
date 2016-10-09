"""
This contains decorators and code to handle pages which require ssl
"""

import logging

from flask import request, redirect, current_app

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


def ssl_required(fn):
    """
    Decorator - marks a route as needing ssl.

    NOTE: This most go BEFORE the route!
    """
    fn.ssl_required = True
    return fn


def handle_ssl_redirect():
    """
    Check if a route needs ssl, and redirect it if not.  Also redirects back to http for non-ssl routes.  Static routes
    are served as both http and https

    :return: A response to be returned or None
    """
    if request.endpoint and request.endpoint != 'static':
        needs_ssl = False
        view_function = current_app.view_functions[request.endpoint]
        if hasattr(view_function, 'ssl_required') and view_function.ssl_required:
            needs_ssl = True

        if current_app.config['SSL_ENABLED']:
            if needs_ssl and not request.is_secure:
                log.debug('Redirecting to https: %s' % request.endpoint)
                return redirect(request.url.replace("http://", "https://"))
            elif not needs_ssl and request.is_secure:
                log.debug('Redirecting to http: %s' % request.endpoint)
                return redirect(request.url.replace("https://", "http://"))
        elif needs_ssl:
            log.info('Not redirecting to HTTPS for endpoint %s as SSL_ENABLED is set to False' % request.endpoint)
