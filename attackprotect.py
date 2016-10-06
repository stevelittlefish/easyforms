"""
Class to prevent brute force attacks on the login
"""

import logging
import datetime
import threading

from .background import systemevent

__author__ = 'Yu Lee Paul (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


class AttackProtect(object):
    def __init__(self, max_attempts, decrease_every, lock_duration):
        """
        :param max_attempts: maximum number of attempts allowed
        :param decrease_every: time (seconds) interval between decreasing attempts
        :param lock_duration: time (seconds) keys are locked for
        :return:
        """
        self.max_attempts = max_attempts
        self.decrease_every = decrease_every
        self.lock_duration = lock_duration

        # Dictionary maps keys onto number of logged attempts
        self.attempts = {}
        # Dictionary maps keys onto lock expiry times
        self.locks = {}
        # Lock object to ensure we don't read and write to this at the same time
        self.lock = threading.Lock()

        # Add system event to decrement counts and expire locks
        systemevent.queue_event(_AttackProtectServiceEvent(self))

    def log_attempt(self, key):
        """
        Log an attempt against key, incrementing the number of attempts for that key and potentially adding a lock to
        the lock table
        """
        with self.lock:
            if key not in self.attempts:
                self.attempts[key] = 1
            else:
                self.attempts[key] += 1

                if self.attempts[key] >= self.max_attempts:
                    log.info('Account %s locked due to too many login attempts' % key)
                    # lock account
                    self.locks[key] = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.lock_duration)

    def is_allowed(self, key):
        """
        :return: True if the key is NOT locked, or false if it is locked
        """
        with self.lock:
            return key not in self.locks

    def service(self):
        """
        Decrease the countdowns, and remove any expired locks.  Should be called once every <decrease_every> seconds.
        """
        with self.lock:
            # Decrement / remove all attempts
            for key in list(self.attempts.keys()):
                log.debug('Decrementing count for %s' % key)
                if key in self.attempts:
                    if self.attempts[key] <= 1:
                        del self.attempts[key]
                    else:
                        self.attempts[key] -= 1

            # Remove expired locks
            now = datetime.datetime.utcnow()
            for key in list(self.locks.keys()):
                if key in self.locks and self.locks[key] < now:
                    log.info('Expiring login lock for %s' % key)
                    del self.locks[key]


class _AttackProtectServiceEvent(systemevent.SystemEvent):
    def __init__(self, attack_protect):
        self.attack_protect = attack_protect
        super(_AttackProtectServiceEvent, self).__init__(run_every=attack_protect.decrease_every)

    def process(self):
        self.attack_protect.service()
