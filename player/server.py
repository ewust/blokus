import ssl
import socket
import logger
import sys

# This should point to the server's self-signed certificate.
# Alternatively, you can use a signed certificate, and 
# point this to /etc/ssl/certs/ca-certificates.crt :)
CA_CERT_FILE='server.crt'

# Client-generated 
CLIENT_CERT_FILE = 'client.crt'
CLIENT_KEY_FILE = 'client.key'

class ServerComm(object):
    def __init__(self, server=("127.0.0.1", 4434)):
        self.server = server

    def join_game(self):
    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Use our client certificate to authenticate to the server.
        self.ssl_sock = ssl.wrap_socket(self.sock, cert_reqs=ssl.CERT_REQUIRED,
                                        ca_certs=CA_CERT_FILE,
                                        certfile=CLIENT_CERT_FILE,
                                        keyfile=CLIENT_KEY_FILE)

        self.ssl_sock.connect(self.server)

        # Send join message?
        pass


    # Call this to wait for the server to send us messages
    def game_loop(self, addr=('127.0.0.1', 4433)):

        data = self.ssl_sock.read()
        while data:
            
            data = self.ssl_sock.read()

 
    def handle_server_stream(self, server_stream):
        data = self.server_stream.read()
        while data:
            print data
            data = self.server_stream.read()
        print 'no more data :('


if __name__ == "__main__":
    # Unit test for server communication

    logger.setLogger(logger.FileLogger(sys.stdout))
    logger.setLogLevel(logger.DEBUG)

    comms = ServerComm(server=("127.0.0.1", 4434))
    comms.join_game()

    #print comms.ssl_sock.getpeercert()
    comms.game_loop()
 
    
