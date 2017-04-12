"""
This contains validation functions.  Each of these functions takes the form value as a parameter, and returns
either an error message, or None if the value passes validation
"""

import logging
import datetime

from littlefish import validation

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


def required(val):
    if val == '' or val is None:
        return 'Required'


def min_value(minimum):
    def f(val):
        if val is not None and val < minimum:
            return 'Must be at least %s' % minimum

    return f


def max_value(maximum):
    def f(val):
        if val is not None and val > maximum:
            return 'Must be less than or equal to %s' % maximum

    return f


def email(val):
    if val and not validation.validate_email_address(val):
        return 'Must be a valid email address'


def url(val):
    if val and not validation.validate_url(val):
        return 'Must be a valid URL starting with http:// or https://'


def phone_number(val):
    if val and not validation.validate_telephone_number(val):
        return 'Must be a valid phone number'


def postcode(val):
    # Does not make sure postcode has a space in it...
    if val and not validation.validate_postcode(val):
        return 'Invalid Postcode'


def must_be_in_past(val):
    if val and val >= datetime.datetime.now().date():
        return 'Must be in the past'


def date_must_not_be_in_past(val):
    if val:
        today = datetime.datetime.now().date()
        if val < today:
            return 'Must not be in the past'


def max_length(length):
    def f(val):
        if val is not None and len(val) > length:
            return 'The maximum length is %s and you entered a string of length %s' % (length, len(val))

    return f


def url_safe(val):
    if val and not validation.validate_url_safe(val):
        return 'Must only contain letters, numbers, hyphens and underscores'

