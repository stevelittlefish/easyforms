"""
Contains field validation functions
"""

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

import logging
import re

log = logging.getLogger(__name__)

email_regex = re.compile('^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z.]+$', flags=re.IGNORECASE)
telephone_regex = re.compile('^\+?\d+(\s*-?\s*\d+)*$')
postcode_regex = re.compile('^[A-Za-z0-9 -]{1,10}$')
url_regex = re.compile('^https?://[^.]+\.[^.]+')


def luhn_check(card_number):
    """ checks to make sure that the card passes a luhn mod-10 checksum """
    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1

    for count in range(0, num_digits):
        digit = int(card_number[count])

        if not ((count & 1) ^ oddeven):
            digit *= 2
        if digit > 9:
            digit -= 9

        sum += digit

    return (sum % 10) == 0


def validate_email_address(email_address):
    return email_regex.match(email_address)


def validate_url(url):
    return url_regex.match(url)


def validate_telephone_number(telephone_number):
    return telephone_regex.match(telephone_number) and len(telephone_number) >= 8


def validate_postcode(postcode):
    return postcode_regex.match(postcode)
