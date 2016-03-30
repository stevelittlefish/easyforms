"""
Code to send email messages via an SMTP server
"""

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

import logging
from email.mime.text import MIMEText
import smtplib
import json
import traceback
import pprint

from app import app

log = logging.getLogger(__name__)

host = app.config['SMTP_HOST']
port = app.config['SMTP_PORT']
username = app.config['SMTP_USERNAME']
password = app.config['SMTP_PASSWORD']
use_tls = app.config['SMTP_USE_TLS']

default_email_from = app.config['DEFAULT_EMAIL_FROM']

# If this is set, we will send all emails here
email_to_override = app.config['EMAIL_TO_OVERRIDE']
# Whether or not to dump the email body
dump_email_body = app.config['DUMP_EMAIL_BODY']


def send_text_mail_single(to_email_address, to_name, subject, body, from_address=None):
    if to_name is None:
        to = to_email_address
    else:
        to = '%s <%s>' % (to_email_address, to_name)

    send_text_mail([to], subject, body, from_address)


def send_text_mail(recipient_list, subject, body, from_address=None):
    """
    :param recipient_list: List of recipients i.e. ['testing@fig14.com', 'Stephen Brown <steve@fig14.com>']
    :param from_address: From email address or name and address i.e. 'Test System <errors@test.com>
    :param subject: The subject
    :param body: The email body
    :return:
    """
    if from_address is None:
        from_address = default_email_from

    log.debug('Sending mail to %s: %s' % (', '.join(recipient_list), subject))
    if dump_email_body:
        log.info(body)

    s = smtplib.SMTP()
    s.connect(host, port)

    if use_tls:
        s.ehlo()
        s.starttls()
        s.ehlo()

    s.login(username, password)

    if email_to_override:
        subject = '[to %s] %s' % (', '.join(recipient_list), subject)
        recipient_list = [email_to_override]
        log.info('Using email override: %s' % ', '.join(recipient_list))

    msg = MIMEText(body, "plain", "utf-8")
    msg['To'] = ', '.join(recipient_list)
    msg['Subject'] = subject
    msg['From'] = from_address

    s.sendmail(from_address, recipient_list, msg.as_string())
    s.quit()


class LfsSmtpHandler(logging.Handler):
    """
    A handler class which sends an SMTP email for each logging event.  This has been customised to (easily) work with
    lfsmailer
    """
    def __init__(self, fromaddr, toaddrs, subject):
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
        if isinstance(toaddrs, basestring):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self._timeout = 5.0

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

    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            msg = self.format(record)

            # Try to append Flask request details
            try:
                from flask import request
                url = request.url
                endpoint = request.endpoint
                args = pprint.pformat(dict(request.args))
                form = pprint.pformat(dict(request.form))

                msg = '%s\nRequest:\n\nurl:      %s\nendpoint: %s\nargs:     %s\nform:     %s\n' % (msg, url, endpoint, args, form)
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

            # Finally send the message!
            send_text_mail(self.toaddrs, self.subject, msg, self.fromaddr)

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def init_error_emails(send_error_emails, send_warning_emails, from_address, to_addresses, subject):
    if send_error_emails or send_warning_emails:
        log.info('Setting up error / warning emails')
        error_handler = LfsSmtpHandler(from_address, to_addresses, subject)

        if send_warning_emails:
            log.info('Sending WARNING emails as well as ERRORs')
            error_handler.setLevel(logging.WARNING)
        else:
            log.info('Only sending ERROR emails')
            error_handler.setLevel(logging.ERROR)

        logging.getLogger().addHandler(error_handler)