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
            while simple_server.running:
                data = self.request.recv(1024)
                if not data:
                    log.debug('Client disconnect')
                    self.request.close()
                    break

                simple_server.add_data(data)

    return SimpleTcpHandler


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class SimpleServer(object):
    def __init__(self, host='localhost', port=49932, print_data=False):
        self.host = host
        self.port = port
        self.print_data = print_data
        self.data = []
        self.data_lock = threading.Lock()
        self.server = ThreadedTCPServer((host, port), simple_tcp_handler(self))
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.running = False

    def start(self):
        self.server_thread.start()
        log.info('Server tread started ({}:{})'.format(self.host, self.port))
        self.running = True

    def stop(self):
        log.info('Shutting down server')
        self.running = False
        self.server.shutdown()
        self.server.server_close()
        log.info('Server shut down complete')

    def add_data(self, value):
        with self.data_lock:
            if self.print_data:
                log.info('Received: {}'.format(value))

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

    server = SimpleServer(port=port, print_data=True)

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


