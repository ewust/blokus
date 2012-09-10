# vim: ts=4 et sw=4 sts=4

import random
import threading

from common.communication import Message
from common.data import Board

from Clear_server import ClearServer as Server

class Game(object):
    def __init__(self, port=None):
        if (port):
            self.server = Server(port)
        else:
            self.server = Server()

        self.lock = threading.Lock()

        self.board = Board()

class BasicGame(Game):
    def __init__(self, port=None):
        self.arrival_sem = threading.Semaphore(0)
        self.go_sem = []
        for i in xrange(4):
            self.go_sem.append(threading.Semaphore(0))

        super(BasicGame, self).__init__()

    def player(self, player_id):
        l = threading.local()
        l.go_sem = self.go_sem[player_id]

        with self.lock:
            l.sock, l.user = self.server.get_connection()

        m = Message(l.sock)
        if not m.match(Message.TYPE_CONTROL, "JOIN"):
            raise
        print "Got JOIN from " + l.user

        Message.serialized(l.sock, Message.TYPE_BOARD, self.board)

        Message.serialized(l.sock, Message.TYPE_CONTROL, "WAIT")

        self.arrival_sem.release()

        while True:
            l.go_sem.acquire()

    def play_game(self):
        players = [0,1,2,3]
        random.shuffle(players)

        t = []

        t.append(threading.Thread(target=self.player, args=(players[0],)))
        t.append(threading.Thread(target=self.player, args=(players[1],)))
        t.append(threading.Thread(target=self.player, args=(players[2],)))
        t.append(threading.Thread(target=self.player, args=(players[3],)))

        for thread in t:
            thread.start()

        for thread in t:
            self.arrival_sem.acquire()

        self.go_sem[0].release()

        for thread in t:
            thread.join()
            print "THREAD DEAD"

if __name__ == '__main__':
    g = BasicGame()
    g.play_game()
