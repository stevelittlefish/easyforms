"""
Contains field validation functions
"""

import logging
import re

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)

email_regex = re.compile('^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z.]+$', flags=re.IGNORECASE)
telephone_regex = re.compile('^\+?\d+(\s*-?\s*\d+)*$')
postcode_regex = re.compile('^[A-Za-z0-9 -]{1,10}$')
url_regex = re.compile('^https?://[^.]+\.[^.]+')
card_number_regex = re.compile('^\d{16}$')
security_code_regex = re.compile('^\d{3}$')
royal_mail_tracking_number_regex = re.compile('^[A-Z0-9]{11}GB$')
url_safe_regex = re.compile('^[A-Za-z0-9_-]+$')


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


def validate_card_number(card_number):
    return card_number_regex.match(card_number)


def validate_security_code(security_code):
    return security_code_regex.match(security_code)


def validate_royal_mail_tracking_number(tracking_number):
    return royal_mail_tracking_number_regex.match(tracking_number)


def validate_url_safe(value):
    return url_safe_regex.match(value)

