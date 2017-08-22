"""
App factory function
"""

import logging
import datetime
import traceback

from flask import Flask, render_template
import jinja2
from littlefish import timetool

from main import main

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

CACHE_BUSTER = int(timetool.unix_time())

log = logging.getLogger(__name__)


def create_app():
    logging.basicConfig(level=logging.DEBUG)

    # Create the webapp
    app = Flask(__name__)
    app.secret_key = 'TestAppSecretKeyWhoCaresWhatThisIs'
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['RECAPTCHA_SITE_KEY'] = 'TODO: Override in config.py'
    app.config['RECAPTCHA_SECRET_KEY'] = 'TODO: Override in config.py'
    
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    log.info(' Test App Starting')
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    
    log.info('Trying to load testapp/config.py...')
    try:
        app.config.from_object('config')
        log.info('Local config loaded')
    except Exception as e:
        log.info('Config not found or invalid')


    # Don't allow output of undefined variables in jinja templates
    app.jinja_env.undefined = jinja2.StrictUndefined
    
    log.info('Registering blueprints')
    app.register_blueprint(main)
    
    @app.context_processor
    def add_global_context():
        return {
            'date': datetime.datetime.now(),
            'CACHE_BUSTER': CACHE_BUSTER
        }

    @app.errorhandler(Exception)
    def catch_all(e):
        title = str(e)
        message = traceback.format_exc()

        log.error('Exception caught: %s\n%s' % (title, message))

        return render_template('error_page.html', title=title, message=message, preformat=True)

    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    log.info(' Startup Complete!')
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    
    return app
