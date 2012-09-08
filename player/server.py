import ssl
import socket
import logger
import sys

# This should point to the server's self-signed certificate.
# Alternatively, you can use a signed certificate, and 
# point this to /etc/ssl/certs/ca-certificates.crt :)
CA_CERT_FILE='server.crt'
CA_CERT_FILE='client.crt'

# Client-generated 
CLIENT_CERT_FILE = 'client.crt'
CLIENT_KEY_FILE = 'client.key'

class ServerComm(object):
    def __init__(self, server=("hobocomp.com", 4433)):
        self.server = server

    def join_game(self):
    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssl_sock = ssl.wrap_socket(self.sock, cert_reqs=ssl.CERT_REQUIRED, \
                                        ca_certs=CA_CERT_FILE)

        self.ssl_sock.connect(self.server)



    # Call this to wait for the server to connect
    def game_loop(self, addr=('127.0.0.1', 4433)):
        self.bindsock = socket.socket()
        self.bindsock.bind(addr)
        self.bindsock.listen(1)
        
        while True:
            newsock, fromaddr = self.bindsock.accept()
            logger.info("Received connection from %s:%d" % (fromaddr)) 
            try:
                self.server_stream = ssl.wrap_socket(newsock,
                                                 server_side=True,
                                                 certfile=CLIENT_CERT_FILE,
                                                 keyfile=CLIENT_KEY_FILE,
                                                 cert_reqs=ssl.CERT_REQUIRED,
                                                 ca_certs=CA_CERT_FILE,
                                                 ssl_version=ssl.PROTOCOL_TLSv1)

            except ssl.SSLError as e:
                logger.error("SSL error: %s" % e)
                continue
                
            logger.debug("SSL cert: %s" % str(self.server_stream.getpeercert()))

            data = self.server_stream.read()
            while data:
                print data
                data = self.server_stream.read()
            print 'no more data :('


if __name__ == "__main__":
    # Unit test for server communication

    logger.setLogger(logger.FileLogger(sys.stdout))
    logger.setLogLevel(logger.DEBUG)

    comms = ServerComm(server=("ericw.us", 443))
    #comms.join_game()

    #print comms.ssl_sock.getpeercert()
    comms.game_loop()
 
    
