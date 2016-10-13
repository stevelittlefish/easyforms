"""
Simple socket server, designed for unit testing
"""

import logging
import socketserver
import threading

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


def simple_tcp_handler(simple_server):
    class SimpleTcpHandler(socketserver.BaseRequestHandler):
        def handle(self):
            data = self.request.recv(1024)
            simple_server.add_data(data)

    return SimpleTcpHandler


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class SimpleServer(object):
    def __init__(self, host='localhost', port=49932):
        self.host = host
        self.port = port
        self.data = []
        self.data_lock = threading.Lock()
        self.server = ThreadedTCPServer((host, port), simple_tcp_handler(self))
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True

    def start(self):
        self.server_thread.start()
        log.info('Server tread started ({}:{})'.format(self.host, self.port))

    def stop(self):
        log.info('Shutting down server')
        self.server.shutdown()
        self.server.server_close()
        log.info('Server shut down complete')

    def add_data(self, value):
        with self.data_lock:
            self.data.append(value.decode('utf-8'))

    def get_data(self):
        with self.data_lock:
            return ''.join(self.data)

    def clear_data(self):
        with self.data_lock:
            self.data = []

    def get_and_clear_data(self):
        with self.data_lock:
            data = ''.join(self.data)
            self.data = []
            return data


if __name__ == '__main__':
    import time
    import datetime
    import signal
    import sys
    
    logging.basicConfig(level=logging.DEBUG)
    
    port = 49932
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    server = SimpleServer(port=port)

    def signal_handler(sig, frame):
        log.info('CTRL+C pressed - shutting down')
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    server.start()
    while (True):
        log.debug('Server still running {}'.format(datetime.datetime.now()))
        data = server.get_and_clear_data()
        if data:
            log.info('Data:\n{}'.format(data))
        time.sleep(10)


