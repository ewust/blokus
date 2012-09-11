# vim: ts=4 et sw=4 sts=4

# TTTA: Can a gui board subclass from a regular board, perhaps replacing the
# underlying Block class to allow for re-drawing? Things are starting to
# duplicate a lot

import pygtk
pygtk.require('2.0')
import gtk

import sys

from common.game_logger import GameParser

__version__ = 0.1

class BlockusBoard:
    def build_menu_line(self):
        self.menu_line_elements = []

        title_string = gtk.Label("Blockus Viewer v" + str(__version__))
        self.menu_line_elements.append(title_string)

        first = gtk.Button(stock=gtk.STOCK_GOTO_FIRST)
        first.connect('clicked', self.goto_move_extreme, -1)
        self.menu_line_elements.append(first)

        back = gtk.Button(stock=gtk.STOCK_GO_BACK)
        back.connect('clicked', self.goto_move_relative, -1)
        self.menu_line_elements.append(back)

        forward = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        forward.connect('clicked', self.goto_move_relative, 1)
        self.menu_line_elements.append(forward)

        last = gtk.Button(stock=gtk.STOCK_GOTO_LAST)
        last.connect('clicked', self.goto_move_extreme, 1)
        self.menu_line_elements.append(last)

        self.turn_id = gtk.Label("Turn 0 / %d" % (len(self.move_history)))
        self.menu_line_elements.append(self.turn_id)

        for e in self.menu_line_elements:
            self.menu_line.pack_start(e)

    def build_board(self):
        fmt = []
        for c in xrange(self.cols):
            fmt.append(gtk.gdk.Pixbuf)
        liststore = gtk.ListStore(*fmt)

        tv_cols = []
        for c in xrange(self.cols):
            tv_cols.append(gtk.TreeViewColumn(str(c)))

        self.blocks = {
                'empty' : gtk.gdk.pixbuf_new_from_file('common/resources/block_empty.png'),
                'red' : gtk.gdk.pixbuf_new_from_file('common/resources/block_red.png'),
                'blue' : gtk.gdk.pixbuf_new_from_file('common/resources/block_blue.png'),
                'green' : gtk.gdk.pixbuf_new_from_file('common/resources/block_green.png'),
                'yellow' : gtk.gdk.pixbuf_new_from_file('common/resources/block_yellow.png'),
                }

        for r in xrange(self.rows):
            row = []
            for c in xrange(self.cols):
                row.append(self.blocks['empty'])
            liststore.append(row)

        treeview = gtk.TreeView(liststore)

        for c in tv_cols:
            treeview.append_column(c)
            cell = gtk.CellRendererPixbuf()
            c.pack_start(cell)
            c.set_attributes(cell, pixbuf=tv_cols.index(c))

        treeview.set_headers_clickable(False)
        treeview.set_rules_hint(False)
        treeview.set_enable_search(False)
        #treeview.set_fixed_height_mode(True)
        treeview.set_headers_visible(False)
        treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_NONE)

        treeview.get_selection().set_mode(gtk.SELECTION_NONE)
        self.board['container'].pack_start(treeview)

        self.board['liststore'] = liststore
        self.board['treeview'] = treeview

    def build_status_line(self):
        self.status_line_elements = []

        self.status_string = gtk.Label("Waiting for new moves...")
        self.status_line_elements.append(self.status_string)

        for e in self.status_line_elements:
            self.status_line.pack_start(e)

    def build_gui(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.board = {}

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.destroy)

        self.vbox = gtk.VBox()
        self.window.add(self.vbox)

        self.menu_line = gtk.HBox()
        self.vbox.pack_start(self.menu_line)
        self.build_menu_line()

        self.vbox.pack_start(gtk.HSeparator())

        self.board['container'] = gtk.VBox()
        self.vbox.pack_start(self.board['container'])
        self.build_board()

        self.vbox.pack_start(gtk.HSeparator())

        self.status_line = gtk.HBox()
        self.vbox.pack_start(self.status_line)
        self.build_status_line()

        self.window.show_all()

    def __init__(self, rows, cols, piece_factory):
        self.piece_factory = piece_factory
        self.shape = (rows, cols)

        self.move_history = []
        self.current_move = -1

        self.build_gui(rows, cols)

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def update_turn_label(self):
        self.turn_id.set_text("Turn %d / %d" % (
            self.current_move + 1,
            len(self.move_history),
            ))

    def id_to_color(self, player_id):
        if player_id == 0:
            return 'red'
        elif player_id == 1:
            return 'blue'
        elif player_id == 2:
            return 'yellow'
        elif player_id == 3:
            return 'green'
        else:
            raise IndexError

    def add_move(self, move):
        self.move_history.append(move)
        self.update_turn_label()

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
        self.update_turn_label()

    def do_move(self, move, new_block):
        self.status_string.set_text('Last move: ' + str(move))

        if move.is_skip():
            return

        piece = self.piece_factory[move.piece_id]
        coords = piece.get_CCW_coords(move.rotation)

        for coord in coords:
            coord += move.position
            treeiter = self.board['liststore'].get_iter((coord.y))
            self.board['liststore'].set_value(treeiter, coord.x, new_block)

    def play_move(self, move):
        new_block = self.blocks[self.id_to_color(move.player_id)]
        self.do_move(move, new_block)

    def unplay_move(self, move):
        new_block = self.blocks['empty']
        self.do_move(move, new_block)

    def main(self):
        gtk.main()

if __name__ == '__main__':
    try:
        game = GameParser(sys.argv[1])
    except IndexError:
        raise NotImplementedError, "Game log required, only reply supported"
    b = BlockusBoard(game.size, game.size, game.piece_factory)
    for move in game:
        b.add_move(move)
    b.main()
