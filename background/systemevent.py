"""
System Event queue is a background thread that runs several repeated tasks in a single thread
"""
import logging
import datetime
import threading
import time

from sqlalchemy.exc import SQLAlchemyError

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)

_SYSTEM_EVENTS = []

_debug = False
_run_interval = None
_min_interval = None
_configured = False


def init(app):
    global _debug, _run_interval, _min_interval, _configured

    if _configured:
        raise Exception('Tried in initialise system events twice!')

    _debug = app.config.get('SYSTEM_EVENT_DEBUG', False)
    _run_interval = app.config['SYSTEM_EVENT_RUN_INTERVAL']
    _min_interval = app.config['SYSTEM_EVENT_MIN_INTERVAL']

    system_event_thread = _SystemEventThread()
    system_event_thread.start()


def queue_event(event):
    log.info('Queueing System Event: %s' % event)
    log.debug('Event will run at %s and then every %s seconds' % (event.next_run, event.run_every))
    _SYSTEM_EVENTS.append(event)


class SystemEvent(object):
    def __init__(self, first_run=None, run_every=None):
        """
        :param first_run: datetime - when this event should first run
        :param run_every: number of seconds between repeats of this task or None for no repeat
        """
        if first_run is None:
            self.next_run = datetime.datetime.utcnow()
        else:
            self.next_run = first_run

        self.run_every = run_every

        self.error = None
        self.done = False

    def run_job(self):
        from models import db

        try:
            if _debug:
                log.info('Running system event: %s' % self)
            self.process()
        except SQLAlchemyError as e:
            log.exception('Database error in system event %s - rolling back to try to recover' % self)
            db.session.rollback()
            self.error = str(e)
        except Exception as e:
            log.exception('Error running system event: %s' % self)
            self.error = str(e)

        if self.run_every:
            interval = datetime.timedelta(seconds=self.run_every)
            self.next_run = datetime.datetime.utcnow() + interval
            if _debug:
                log.info('Next run in %s at %s' % (interval, self.next_run))
        else:
            self.done = True

    def process(self):
        raise NotImplementedError()


class _SystemEventThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        from models import db
        global _SYSTEM_EVENTS

        log.info('System event thread starting up')
        log.info('Checking for system events every %s seconds' % _run_interval)

        # Start the loop
        while True:
            # Default to run_interval in case we crash
            sleep_time = _run_interval

            try:
                if _debug:
                    log.info('System Event Queue - waking up')
                now = datetime.datetime.utcnow()

                # Load all of the pending cron jobs
                for job in _SYSTEM_EVENTS:
                    if job.next_run < now:
                        job.run_job()

                _SYSTEM_EVENTS = [job for job in _SYSTEM_EVENTS if not job.done]

                # Now that we've run all jobs, calculate the next run time
                dt = datetime.datetime.utcnow() - now
                if _debug:
                    log.info('System event cycle took %s' % dt)
                sleep_time -= dt.seconds
                if sleep_time < _min_interval:
                    log.warning('System event cycle took too long!  Took %s when desired interval is %s seconds'
                                % (dt, _run_interval))
                    sleep_time = _min_interval

            except SQLAlchemyError:
                log.exception('Database error in System event thread - rolling back to try to recover')
                db.session.rollback()

            except Exception:
                log.exception('Error in System event thread')

            if _debug:
                log.info('Sleeping for %s seconds' % sleep_time)
            time.sleep(sleep_time)

        log.info('System event thread shutting down')
