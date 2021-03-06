"""
App factory function
"""

import logging
import datetime
import traceback

from flask import Flask, render_template
import jinja2
from littlefish import timetool
import flaskfilemanager

from main import main
import sessionutil

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
    app.config['GETADDRESS_API_KEY'] = 'TODO: Override in config.py'
    app.config['FILEMANAGER_ENABLED'] = True
    app.config['FLASKFILEMANAGER_FILE_PATH'] = 'tmp-webapp-uploads'
    
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    log.info(' Test App Starting')
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    
    log.info('Trying to load testapp/config.py...')
    try:
        app.config.from_object('config')
        log.info('Local config loaded')
    except Exception:
        log.info('Config not found or invalid')

    # Don't allow output of undefined variables in jinja templates
    app.jinja_env.undefined = jinja2.StrictUndefined
    
    log.info('Registering blueprints')
    app.register_blueprint(main)
    
    @app.context_processor
    def add_global_context():
        render_style = sessionutil.get_render_style()

        return {
            'date': datetime.datetime.now(),
            'CACHE_BUSTER': CACHE_BUSTER,
            'base_template': 'base_{}.html'.format(render_style),
            'render_style': render_style
        }

    @app.errorhandler(Exception)
    def catch_all(e):
        title = str(e)
        message = traceback.format_exc()

        log.error('Exception caught: %s\n%s' % (title, message))

        return render_template('error_page.html', title=title, message=message, preformat=True)
    
    log.info('Initialising Filemanager')
    def fm_access_control():
        """
	:return: True if the user is allowed to access the filemanager, otherwise False
	"""
        return app.config['FILEMANAGER_ENABLED']

    flaskfilemanager.init(app, access_control_function=fm_access_control)

    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    log.info(' Startup Complete!')
    log.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    
    return app
