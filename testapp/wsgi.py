"""
WSGI Entry Point (for gunicorn)
"""

from werkzeug.contrib.fixers import ProxyFix

from app import create_app

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

application = create_app()
application.wsgi_app = ProxyFix(application.wsgi_app)

