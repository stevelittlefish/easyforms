"""
The form in here is idential to the usual Form - but defaults to bootstrap 4 without having
to pass the bootstrap version in
"""

import logging

from . import Form as BaseForm
from . import styles

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


class Form(BaseForm):
    def __init__(self, *args, **kwargs):
        if 'style' in kwargs:
            raise ValueError('You can\'t set a bootstrap version with this BS4 only form!')
        
        kwargs['style'] = styles.BOOTSTRAP_4

        super().__init__(*args, **kwargs)


