# vim: ts=4 et sw=4 sts=4

import socket
import errno

class Clear_Connection(object):

    def __init__(self, server=("127.0.0.1", 4080)):
        self.server = server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(self.server)
        except socket.error as exc:
            if exc.errno is errno.ECONNREFUSED:
                print "XXX\nDo something smarter, loop, wait?\nXXX\n"
                raise exc

    def get_socket(self):
        return self.sock

if __name__ == "__main__":
    # Unit test for server communication

    logger.setLogger(logger.FileLogger(sys.stdout))
    logger.setLogLevel(logger.DEBUG)

    conn = Clear_Connection(server=("127.0.0.1", 4080))
    conn.connect()

