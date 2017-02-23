"""
Code to send email messages via an SMTP server
"""

import logging
from email.mime.text import MIMEText
import smtplib
import json
import traceback
import pprint
import email.utils

from . import timetool

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)

host = None
port = None
username = None
password = None
use_tls = None
default_email_from = None
email_to_override = None
dump_email_body = None
_configured = False


def init(app):
    global host, port, username, password, use_tls, default_email_from, email_to_override,\
        dump_email_body, _configured

    if _configured and not app.config['TESTING']:
        raise Exception('Multiple calls to {}.init(app)'.format(__name__))

    host = app.config['SMTP_HOST']
    port = app.config['SMTP_PORT']
    username = app.config['SMTP_USERNAME']
    password = app.config['SMTP_PASSWORD']
    use_tls = app.config['SMTP_USE_TLS']

    log.info('LFS Mailer using {}@{}:{}{}'.format(username, host, port, ' (TLS)' if use_tls else ''))

    default_email_from = app.config['DEFAULT_EMAIL_FROM']

    # If this is set, we will send all emails here
    email_to_override = app.config['EMAIL_TO_OVERRIDE']
    # Whether or not to dump the email body
    dump_email_body = app.config['DUMP_EMAIL_BODY']

    _configured = True


def format_address(email_address, name=None):
    if name is None:
        return email_address
    return '{} <{}>'.format(name, email_address)


def send_text_mail_single(to_email_address, to_name, subject, body, from_address=None):
    to = format_address(to_email_address, to_name)

    send_text_mail([to], subject, body, from_address)


def send_text_mail(recipient_list, subject, body, from_address=None):
    send_mail(recipient_list, subject, body, html=False, from_address=from_address)


def send_html_mail_single(to_email_address, to_name, subject, body, from_address=None):
    to = format_address(to_email_address, to_name)

    send_html_mail([to], subject, body, from_address)


def send_html_mail(recipient_list, subject, body, from_address=None):
    send_mail(recipient_list, subject, body, html=True, from_address=from_address)


def send_mail(recipient_list, subject, body, html=False, from_address=None):
    """
    :param recipient_list: List of recipients i.e. ['testing@fig14.com', 'Stephen Brown <steve@fig14.com>']
    :param subject: The subject
    :param body: The email body
    :param html: Is this a html email? Defaults to False
    :param from_address: From email address or name and address i.e. 'Test System <errors@test.com>
    :return:
    """
    if not _configured:
        raise Exception('LFS Mailer hasn\'t been configured')

    if from_address is None:
        from_address = default_email_from
    
    mime_type = 'html' if html else 'plain'
    log.debug('Sending {} mail to {}: {}'.format(mime_type, ', '.join(recipient_list), subject))
    if dump_email_body:
        log.info(body)

    s = smtplib.SMTP(host, port)

    if use_tls:
        s.ehlo()
        s.starttls()
        s.ehlo()
    
    if username:
        s.login(username, password)

    if email_to_override:
        subject = '[to %s] %s' % (', '.join(recipient_list), subject)
        recipient_list = [email_to_override]
        log.info('Using email override: %s' % ', '.join(recipient_list))

    msg = MIMEText(body, mime_type, 'utf-8')
    msg['To'] = ', '.join(recipient_list)
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['Date'] = email.utils.formatdate()

    s.sendmail(from_address, recipient_list, msg.as_string())
    s.quit()


class LfsSmtpHandler(logging.Handler):
    """
    A handler class which sends an SMTP email for each logging event.  This has been customised to (easily) work with
    lfsmailer
    """
    def __init__(self, fromaddr, toaddrs, subject, max_sends_per_minute=15):
        """
        Initialize the handler.

        Initialize the instance with the from and to addresses and subject
        line of the email. To specify a non-standard SMTP port, use the
        (host, port) tuple format for the mailhost argument. To specify
        authentication credentials, supply a (username, password) tuple
        for the credentials argument. To specify the use of a secure
        protocol (TLS), pass in a tuple for the secure argument. This will
        only be used when authentication credentials are supplied. The tuple
        will be either an empty tuple, or a single-value tuple with the name
        of a keyfile, or a 2-value tuple with the names of the keyfile and
        certificate file. (This tuple is passed to the `starttls` method).
        """
        super(LfsSmtpHandler, self).__init__()
        self.fromaddr = fromaddr
        if isinstance(toaddrs, str):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self._timeout = 5.0
        self.max_sends_per_minute = max_sends_per_minute
        self.rate_limiter = []

        # Default formatter
        self.setFormatter(logging.Formatter('''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''))
    
    def add_details(self, message):
        """
        Add extra details to the message.  Separate so that it can be overridden
        """
        msg = message
        # Try to append Flask request details
        try:
            from flask import request
            url = request.url
            method = request.method
            endpoint = request.endpoint

            # Obscure password field and prettify a little bit
            form_dict = dict(request.form)
            for key in form_dict:
                if 'password' in key.lower():
                    form_dict[key] = '******'
                elif len(form_dict[key]) == 1:
                    form_dict[key] = form_dict[key][0]

            form = pprint.pformat(form_dict).replace('\n', '\n          ')

            msg = '%s\nRequest:\n\nurl:      %s\nmethod:   %s\nendpoint: %s\nform:     %s\n' % \
                (msg, url, method, endpoint, form)
        except:
            traceback.print_exc()

        # Try to append the session
        try:
            from flask import session
            from flask.json import JSONEncoder
            session_str = json.dumps(
                dict(**session),
                indent=2,
                cls=JSONEncoder
            )
            msg = '%s\nSession:\n\n%s\n' % (msg, session_str)
        except:
            traceback.print_exc()
        
        return msg

    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            # First, remove all records from the rate limiter list that are over a minute old
            now = timetool.unix_time()
            one_minute_ago = now - 60
            new_rate_limiter = [x for x in self.rate_limiter if x > one_minute_ago]
            log.debug('Rate limiter %s -> %s' % (len(self.rate_limiter), len(new_rate_limiter)))
            self.rate_limiter = new_rate_limiter

            # Now, get the number of emails sent in the last minute.  If it's less than the threshold, add another
            # entry to the rate limiter list
            recent_sends = len(self.rate_limiter)
            send_email = recent_sends < self.max_sends_per_minute
            if send_email:
                self.rate_limiter.append(now)

            msg = self.format(record)
            msg = self.add_details(msg)

            # Finally send the message!
            if send_email:
                send_text_mail(self.toaddrs, self.subject, msg, self.fromaddr)
            else:
                log.info('!! WARNING: Not sending email as too many emails have been sent in the past minute !!')
                log.info(msg)

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def init_error_emails(send_error_emails, send_warning_emails, from_address, to_addresses, subject, logger=None):
    if send_error_emails or send_warning_emails:
        log.info('Setting up error / warning emails')
        error_handler = LfsSmtpHandler(from_address, to_addresses, subject)

        if send_warning_emails:
            log.info('Sending WARNING emails as well as ERRORs')
            error_handler.setLevel(logging.WARNING)
        else:
            log.info('Only sending ERROR emails')
            error_handler.setLevel(logging.ERROR)
        
        if logger is None:
            logger = logging.getLogger()

        logger.addHandler(error_handler)
