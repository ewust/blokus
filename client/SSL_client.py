# vim: ts=4 et sw=4 sts=4

import ssl
import socket
import sys

from common import logger

# This should point to the server's self-signed certificate.
# Alternatively, you can use a signed certificate, and 
# point this to /etc/ssl/certs/ca-certificates.crt :)
CA_CERT_FILE='server.crt'

# Client-generated certificate (use ./make_cert.sh)
CLIENT_CERT_FILE = 'client.crt'
CLIENT_KEY_FILE = 'client.key'

class SSL_Connection(object):

    def __init__(self, server=("127.0.0.1", 4434)):
        self.server = server

    """Connects and authenticates to server"""
    def connect(self):
    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Use our client certificate to authenticate to the server.
        self.ssl_sock = ssl.wrap_socket(self.sock, cert_reqs=ssl.CERT_REQUIRED,
                                        ca_certs=CA_CERT_FILE,
                                        certfile=CLIENT_CERT_FILE,
                                        keyfile=CLIENT_KEY_FILE)

        self.ssl_sock.connect(self.server)

    def get_socket(self):
        return self.ssl_sock

if __name__ == "__main__":
    # Unit test for server communication

    logger.setLogger(logger.FileLogger(sys.stdout))
    logger.setLogLevel(logger.DEBUG)

    conn = SSL_Connection(server=("127.0.0.1", 4434))
    conn.connect()

