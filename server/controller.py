# vim: ts=4 et sw=4 sts=4

import random
import threading

from common.communication import Message
from common.data import Board
from common.bot import Bot

from Clear_server import ClearServer as Server

class Game(object):
    class GameError(Exception):
        pass

    class InitializationError(GameError):
        pass

    def __init__(self, port=None):
        if (port):
            self.server = Server(port)
        else:
            self.server = Server()

        self.lock = threading.Lock()

        try:
            self.board
        except NameError:
            raise InitializationError, "Game subclass must define a board"

class BasicGame(Game):
    def __init__(self, port=None):
        self.arrival_sem = threading.Semaphore(0)
        self.go_sem = []
        self.socks = [0,0,0,0]
        self.done = False
        for i in xrange(4):
            self.go_sem.append(threading.Semaphore(0))

        self.board = Board('original')

        super(BasicGame, self).__init__()

    def player(self, player_id):
        l = threading.local()
        l.others = None

        with self.lock:
            l.sock, l.user = self.server.get_connection()
            self.socks[player_id] = l.sock

        m = Message(l.sock)
        if not m.match(Message.TYPE_CONTROL, "JOIN"):
            raise
        print "Got JOIN from " + l.user

        Message.serialized(l.sock, Message.TYPE_ID, player_id)
        Message.serialized(l.sock, Message.TYPE_BOARD, self.board)

        Message.serialized(l.sock, Message.TYPE_CONTROL, "WAIT")

        self.arrival_sem.release()

        while True:
            self.go_sem[player_id].acquire()

            if self.done:
                break

            Message.serialized(l.sock, Message.TYPE_CONTROL, "TURN")
            m = Message(l.sock, Message.TYPE_MOVE)
            move = m.message_object

            if not self.board.is_valid_move(move):
                Message.serialized(l.sock, Message.TYPE_STATUS,\
                        [Bot.STATUS_SKIPPED, "Illegal Move"])
                self.done = True
                for s in self.go_sem:
                    s.release()

            print repr(move)
            self.board.play_move(move)

            if l.others is None:
                l.others = list(self.socks)
                l.others.pop(player_id)

            for s in l.others:
                Message.serialized(s, Message.TYPE_MOVE, m.message_object)

            self.go_sem[(player_id+1) % 4].release()

        Message.serialized(l.sock, Message.TYPE_STATUS,\
                [Bot.STATUS_GAME_OVER, "This game has ended"])

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
