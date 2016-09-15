"""
Contains a queue of email messages to be sent asynchronously
"""

import logging
import datetime
import traceback

from . import systemevent
from models import db, QueuedEmail
from lfs import timetool
from lfs import lfsmailer

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)

STATUS_QUEUED = 'QUEUED'
STATUS_SENDING = 'SENDING'
STATUS_SENT = 'SENT'
STATUS_FAILED = 'FAILED'
STATUS_RETRY = 'RETRY'


class ProcessEmailQueueSystemEvent(systemevent.SystemEvent):
    def __init__(self, app):
        run_every = app.config['PROCESS_EMAIL_QUEUE_INTERVAL']
        first_run = datetime.datetime.utcnow() + datetime.timedelta(seconds=run_every)

        super(ProcessEmailQueueSystemEvent, self).__init__(run_every=run_every, first_run=first_run)

        self.max_attempts = app.config['EMAIL_QUEUE_MAX_ATTEMPTS']

    def process(self):
        queued_emails = QueuedEmail.query.filter(db.or_(QueuedEmail.status == STATUS_QUEUED,
                                                        QueuedEmail.status == STATUS_RETRY)).all()
        for email in queued_emails:
            email.status = STATUS_SENDING
            email.attempts += 1
            db.session.commit()
            try:
                recipients = [s.strip() for s in email.to_addresses.split(',')]
                lfsmailer.send_mail(recipients, email.subject, email.body, html=email.html,
                                    from_address=email.from_address)
                email.status = STATUS_SENT
                db.session.commit()
            except Exception as e:
                if email.attempts < self.max_attempts:
                    stack_trace = traceback.format_exc()

                    log.warning('Email attempt failed, retrying. Exception: %s\n%s' % (e, stack_trace))
                    email.status = STATUS_RETRY
                    db.session.commit()
                else:
                    log.exception('Email sending failed. Max retries exceeded')
                    email.status = STATUS_FAILED
                    db.session.commit()


class EmailQueueCleanUpSystemEvent(systemevent.SystemEvent):
    def __init__(self, app):
        super(EmailQueueCleanUpSystemEvent, self).__init__(run_every=app.config['CLEAN_UP_EMAIL_QUEUE_INTERVAL'])

        self.max_age = app.config['EMAIL_QUEUE_MAX_DAYS']

    def process(self):
        max_age = datetime.timedelta(days=self.max_age)
        delete_time = datetime.datetime.utcnow() - max_age
        log.info('Cleaning up emails queued before %s' % timetool.format_datetime_long(delete_time))
        num_deleted = QueuedEmail.query.filter(QueuedEmail.timestamp < delete_time).delete()
        db.session.commit()
        log.info('Deleted %s emails' % num_deleted)


def queue_email(to_addresses, from_address, subject, body, commit=True, html=True, session=None):
    """
    Add a mail to the queue to be sent.

    WARNING: Commits by default!

    :param to_addresses: The names and addresses to send the email to, i.e. "Steve<steve@fig14.com>, info@fig14.com"
    :param from_address: Who the email is from i.e. "Stephen Brown <s@fig14.com>"
    :param subject: The email subject
    :param body: The html / text body of the email
    :param commit: Whether to commit to the database
    :param html: Is this a html email?
    :param session: The sqlalchemy session or None to use db.session
    """
    from models import QueuedEmail

    if session is None:
        session = db.session

    log.info('Queuing mail to %s: %s' % (to_addresses, subject))
    queued_email = QueuedEmail(html, to_addresses, from_address, subject, body, STATUS_QUEUED)
    session.add(queued_email)
    session.commit()

    return queued_email


def queue_html_email(to_addresses, from_address, subject, body, commit=True, session=None):
    return queue_email(to_addresses, from_address, subject, body, commit=commit, html=True, session=session)


def queue_text_email(to_addresses, from_address, subject, body, commit=True, session=None):
    return queue_email(to_addresses, from_address, subject, body, commit=commit, html=False, session=session)

