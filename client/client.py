# vim: ts=4 et sw=4 sts=4

import sys
import ConfigParser

from comm import GameServer
from bots.dummybot import DummyBot as MyBot

#from SSL_client import SSL_Connection as Connection
from Clear_client import Clear_Connection as Connection

class Client():
    def _get_default_config(self):
        c = ConfigParser.SafeConfigParser({'server_host':'127.0.0.1', 'server_port':'4080'})
        return c

    def __init__(self, conf=None):
        self.config = self._get_default_config()

        if conf:
            self.config.read(conf)

        server = (self.config.get('DEFAULT', 'server_host'), self.config.getint('DEFAULT', 'server_port'))
        self.server = GameServer(connection=Connection(server))

    def play_game(self):
        player_id, board = self.server.join_game()
        self.bot = MyBot(player_id=player_id, board=board)
        while (self.server.game_loop(self.bot)):
            pass

    def go(self):
        while True:
            self.play_game()

if __name__ == '__main__':
    # XXX: Write unit tests?
    Client().play_game()
