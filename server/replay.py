# vim: ts=4 et sw=4 sts=4

import sys

from common.gui import BoardGui
from common.game_logger import GameParser

__version__ = 0.1

class ReplayGui(BoardGui):
    def build_menu_line(self):
        self.menu_line_elements = []

        title_string = Gtk.Label(label="Replay Viewer v" + str(__version__))
        self.menu_line_elements.append(title_string)

        first = Gtk.Button(stock=Gtk.STOCK_GOTO_FIRST)
        first.connect('clicked', self.goto_move_extreme, -1)
        self.menu_line_elements.append(first)

        back = Gtk.Button(stock=Gtk.STOCK_GO_BACK)
        back.connect('clicked', self.goto_move_relative, -1)
        self.menu_line_elements.append(back)

        forward = Gtk.Button(stock=Gtk.STOCK_GO_FORWARD)
        forward.connect('clicked', self.goto_move_relative, 1)
        self.menu_line_elements.append(forward)

        last = Gtk.Button(stock=Gtk.STOCK_GOTO_LAST)
        last.connect('clicked', self.goto_move_extreme, 1)
        self.menu_line_elements.append(last)

        self.turn_id = Gtk.Label(label="Turn 0 / %d" % (len(self.move_history)))
        self.menu_line_elements.append(self.turn_id)

        for e in self.menu_line_elements:
            self.menu_line.pack_start(e, True, True, 0)

    def goto_move_extreme(self, button, direction):
        try:
            while True:
                self.goto_move_relative(None, direction)
        except IndexError:
            pass

    def goto_move_relative(self, button, increment):
        while increment > 0:
            self.play_move(self.move_history[self.current_move+1])
            self.current_move += 1
            increment -= 1
        while increment < 0:
            if self.current_move < 0:
                raise IndexError, "negative indicies out of range"
            self.unplay_move(self.move_history[self.current_move])
            self.current_move -= 1
            increment += 1
        self.update_labels()

if __name__ == '__main__':
    try:
        game = GameParser(sys.argv[1])
    except IndexError as e:
        print "USAGE:"
        print sys.argv[0] + ' game.log'
        sys.exit(1)
    b = BoardGui(shape=game.shape, library=game.library)
    for move in game:
        b.add_move(move)
    b.main()
