# vim: ts=4 et sw=4 sts=4

import random
import threading

from common.communication import Message

from Clear_server import ClearServer as Server

class Game(object):
    def __init__(self, port=None):
        if (port):
            self.server = Server(port)
        else:
            self.server = Server()

        self.lock = threading.Lock()

class BasicGame(Game):
    def player(self, player_id):
        l = threading.local()

        with self.lock:
            l.sock, l.user = self.server.get_connection()

        m = Message(l.sock)
        if not m.match(Message.TYPE_CONTROL, "JOIN"):
            raise
        print "Got JOIN"

        from time import sleep
        while True:
            Message.serialized(l.sock, Message.TYPE_CONTROL, "WAIT")
            sleep(1)

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
            thread.join()
            print "THREAD DEAD"

if __name__ == '__main__':
    g = BasicGame()
    g.play_game()
