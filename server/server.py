from twisted.internet import ssl, reactor
from twisted.internet.protocol import Factory, Protocol
from OpenSSL import SSL
import OpenSSL
import logger
import sys

SERVER_CERT_FILE='server.crt'
SERVER_KEY_FILE='server.key'

# A directory where we store the self-signed certificates
# for each player
CLIENT_CERT_DIR='./player_certs/'
CLIENT_CERTS_FILE='./player_certs/all.crt'



class GameListener(Protocol):

    def __init__(self):
        pass
    def connectionMade(self):
        peer = self.transport.getPeer()
        logger.info("Connection from %s:%d" % (peer.host, peer.port))

        # Set this so verifyCallback can call us when it's done
        self.transport.getHandle().set_app_data(self)

    # Called by verifyCallback
    def verificationComplete(self, user, fingerprint=None):
        peer = self.transport.getPeer()
        logger.info("%s:%d is '%s' (%s)" % (peer.host, peer.port, user, fingerprint))
        self.user = user
        self.fingerprint = fingerprint

    def dataReceived(self, data):
        """As soon as any data is received, write it back."""
        print data
        self.transport.write(data)

    def connectionLost(self):
        peer = self.transport.getPeer()
        logger.info("Connection %s:%d (%s) lost" % (peer.host, peer.port, self.user))

# Because pyOpenSSL doesn't do this,
# we'll use M2Crypto instead (sigh...)
def cert_fingerprint(x509_obj):
    import M2Crypto
    crt_str = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, x509_obj)
    return M2Crypto.X509.load_cert_string(crt_str).get_fingerprint()

def verifyCallback(connection, x509, errnum, errdepth, ok):
    user = x509.get_subject().commonName
    user = user.lower().strip()


    if not ok:
        # if we haven't seen CN before (username),
        # add them to our CLIENT_CERTS_FILE and return True
        trusted_certs_str = open(CLIENT_CERTS_FILE, 'r').read()

        # Ugly, ugly, bad hack, because M2Crypto and pyOpenSSL 
        # didn't figure out how to either 1) trust a directory of certs
        # or 2) load a single file with multiple certs into an array of
        # X509 objects.
        END_CERT_SENTINAL = '-----END CERTIFICATE-----\n'
        for cert_str in trusted_certs_str.split(END_CERT_SENTINAL):
            if (cert_str.strip() == ''):
                break

            cert_str += END_CERT_SENTINAL

            logger.trace('Loading certificate: \n%s' % cert_str)

            cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_str)
            cert_user = cert.get_subject().commonName

            logger.debug("Cert Store: User '%s' %s" % (cert_user, cert_fingerprint(cert)))
            
            if cert_user.lower().strip() == user.lower().strip():
                # User already in cert store, error
                logger.error("User '%s' already in cert store; rejecting" % user)
                logger.debug("User '%s' == '%s'" % (user, cert_user))
                logger.debug("Digest %s , %s already in store" % \
                             (cert_fingerprint(x509), cert_fingerprint(cert)))

                return False

        # User not already in cert store; add them
        x509_str = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, x509)
        with open(CLIENT_CERTS_FILE, 'a') as f:
            f.write(x509_str)

        # Reload the cert store
        connection.get_context().load_verify_locations(CLIENT_CERTS_FILE, None)
        
        logger.info("Added user '%s' to cert store, fingerprint %s" % \
                    (user, cert_fingerprint(x509)))

        # This verify function will get called again with ok == True
        return True

    game_listener = connection.get_app_data()
    if game_listener:
        game_listener.verificationComplete(user, cert_fingerprint(x509))
    logger.debug("User '%s' authenticated (%s)" % (user, cert_fingerprint(x509)))
    return True

if __name__ == '__main__':
    logger.setLogger(logger.FileLogger(sys.stdout))
    logger.setLogLevel(logger.DEBUG)

    factory = Factory()
    factory.protocol = GameListener
    

    ctx_factory = ssl.DefaultOpenSSLContextFactory(SERVER_KEY_FILE,
                                                   SERVER_CERT_FILE)
    ctx = ctx_factory.getContext()
    ctx.set_verify(
        SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
        verifyCallback
        )
    ctx.load_verify_locations(CLIENT_CERTS_FILE, CLIENT_CERT_DIR)
     
    reactor.listenSSL(4434, factory, ctx_factory)
    reactor.run()
