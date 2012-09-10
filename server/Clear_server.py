# vim: ts=4 et sw=4 sts=4

import socket

class ClearServer(object):

    def __init__(self, port=4080):
        self.server = ("", port)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(self.server)
        s.listen(10)
        self.sock = s

        self.hacks = []

    def addr_to_username(self, addr):
        # XXX Handled in SSL by certs, etc, need a parallel
        try:
            return "uniq" + str(self.hacks.index(addr))
        except ValueError:
            self.hacks.append(addr)
            return self.addr_to_username(addr)

    def get_connection(self):
        conn, addr = self.sock.accept()
        return (conn, self.addr_to_username(addr))

