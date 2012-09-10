# vim: ts=4 et sw=4 sts=4

import sys
import ConfigParser

from comm import ServerConnection
from bots.dummybot import DummyBot as MyBot

class Client():
    def __init__(self, conf=None):
        if (conf):
            self.config = ConfigParser.SafeConfigParser()
            self.config.read(conf)

        self.server = ServerConnection()

    def go(self):
        while True:
            player_id, board = self.server.join_game()
            self.bot = MyBot(player_id=player_id, board=board)
            while (self.server.game_loop(self.bot)):
                pass

if __name__ == '__main__':
    # XXX: Write unit tests?
    Client().go()
