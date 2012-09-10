# vim: ts=4 et sw=4 sts=4

import sys
import ConfigParser

from comm import ServerConnection
from bots.dummybot import DummyBot as Bot

class Client():
    def __init__(self, conf=None):
        if (conf):
            self.config = ConfigParser.SafeConfigParser()
            self.config.read(conf)

        self.server = ServerConnection()

    def go(self):
        while True:
            self.bot = Bot()
            self.server.join_game()
            while (self.server.game_loop(self.bot)):
                pass

if __name__ == '__main__':
    # XXX: Write unit tests?
    Client().go()
