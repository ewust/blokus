# vim: ts=4 et sw=4 sts=4

# TTTA: Can a gui board subclass from a regular board, perhaps replacing the
# underlying Block class to allow for re-drawing? Things are starting to
# duplicate a lot

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GdkPixbuf

from common.data import Block,Board,Piece,PieceFactory

__version__ = 0.1

class BlockGui(Block):
    pixbufs = {
            'empty' : GdkPixbuf.Pixbuf.new_from_file('common/resources/block_empty.png'),
            'blue' : GdkPixbuf.Pixbuf.new_from_file('common/resources/block_blue.png'),
            'yellow' : GdkPixbuf.Pixbuf.new_from_file('common/resources/block_yellow.png'),
            'red' : GdkPixbuf.Pixbuf.new_from_file('common/resources/block_red.png'),
            'green' : GdkPixbuf.Pixbuf.new_from_file('common/resources/block_green.png'),
            }

    def get_pixbuf(self):
        try:
            return BlockGui.pixbufs[self.id_to_color(self.move.player_id)]
        except AttributeError as e:
            return BlockGui.pixbufs['empty']

    def id_to_color(self, player_id):
        if player_id == 0:
            return 'blue'
        elif player_id == 1:
            return 'yellow'
        elif player_id == 2:
            return 'red'
        elif player_id == 3:
            return 'green'
        else:
            raise IndexError

class BlockRenderer(Gtk.CellRendererPixbuf):
    __gproperties__ = {
            'block' : (GObject.TYPE_PYOBJECT,
                'block to render',
                'the block object to be rendered',
                GObject.PARAM_READWRITE)
            }

    def __init__(self):
        GObject.GObject.__init__(self)
        self.block = None

    def do_set_property(self, prop, value):
        # What is a GParamBoxed?? (prop is one of those...)
        if isinstance(value, BlockGui):
            self.block = value
            self.set_property('pixbuf', self.block.get_pixbuf())
        elif isinstance(value, Block):
            raise TypeError, "BlockGui required, not Block"

GObject.type_register(BlockRenderer)


class PieceFactoryGui(PieceFactory):
    def _build_piece(self, piece_id, from_str):
        return PieceGui(piece_id=piece_id, from_str=from_str)

class BoardGui(Board):
    def build_menu_line(self):
        self.menu_line_elements = []

        title_string = Gtk.Label(label="Blockus Viewer v" + str(__version__))
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

    def build_board(self):
        self.board = {}

        fmt = []
        for c in xrange(self.cols):
            fmt.append(GObject.TYPE_PYOBJECT)
        liststore = Gtk.ListStore(*fmt)

        for r in xrange(self.rows):
            row = []
            for c in xrange(self.cols):
                row.append(BlockGui())
            liststore.append(row)

        treeview = Gtk.TreeView(liststore)

        for col in xrange(self.cols):
            c = Gtk.TreeViewColumn(str(c))
            treeview.append_column(c)
            cell = BlockRenderer()
            c.pack_start(cell, True)
            c.add_attribute(cell, 'block', col)

        treeview.set_headers_clickable(False)
        treeview.set_rules_hint(False)
        treeview.set_enable_search(False)
        #treeview.set_fixed_height_mode(True)
        treeview.set_headers_visible(False)
        # I can't find the proper resolution to assign this directly?
        g = treeview.get_grid_lines()
        treeview.set_grid_lines(g.NONE)

        treeview.get_selection().set_mode(Gtk.SelectionMode.NONE)

        self.board['liststore'] = liststore
        self.board['treeview'] = treeview
        self.board['container'] = Gtk.VBox()

        self.board['container'].pack_start(treeview, True, True, 0)

    def build_status_line(self):
        self.status_line_elements = []

        self.status_string = Gtk.Label(label="Waiting for new moves...")
        self.status_line_elements.append(self.status_string)

        for e in self.status_line_elements:
            self.status_line.pack_start(e, True, True, 0)

    def build_board_area_box(self):
        self.board_area_box = Gtk.HBox()

        # Left Pane: The Game
        self.game_vbox = Gtk.VBox()
        self.board_area_box.add(self.game_vbox)

        self.menu_line = Gtk.HBox()
        self.game_vbox.pack_start(self.menu_line, True, True, 0)
        self.build_menu_line()

        self.game_vbox.pack_start(Gtk.HSeparator(), True, True, 0)

        self.game_vbox.pack_start(self.board['container'], True, True, 0)

        self.game_vbox.pack_start(Gtk.HSeparator(), True, True, 0)

        self.status_line = Gtk.HBox()
        self.game_vbox.pack_start(self.status_line, True, True, 0)
        self.build_status_line()

        # Divider..
        self.board_area_box.add(Gtk.VSeparator())

        # Right pane: Remaining piece library
        self.pieces_vbox = Gtk.VBox()
        self.board_area_box.add(self.pieces_vbox)

    def get_top_level_box(self):
        return self.board_area_box

    def __init__(self, **kwds):
        super(BoardGui, self).__init__(**kwds)

        self.move_history = []
        self.current_move = -1

        self.build_board_area_box()

        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.connect("destroy", self.destroy)
        self.window.add(self.get_top_level_box())
        self.window.show_all()


    def destroy(self, widget, data=None):
        Gtk.main_quit()

    def update_labels(self):
        self.turn_id.set_text("Turn %d / %d" % (
            self.current_move + 1,
            len(self.move_history),
            ))
        if self.current_move > -1:
            move = self.move_history[self.current_move]
            self.status_string.set_text('Last move: ' + str(move))
        else:
            self.status_string.set_text('No moves played')

    def add_move(self, move):
        self.move_history.append(move)
        self.update_labels()

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

    def do_move(self, move, unplay=False):
        if move.is_skip():
            return

        piece = self.piece_factory[move.piece_id]
        coords = piece.get_CCW_coords(move.rotation)

        for coord in coords:
            coord += move.position
            treeiter = self.board['liststore'].get_iter((coord.y))
            block = self.board['liststore'].get_value(treeiter, coord.x)
            if unplay:
                block.move = None
            else:
                block.move = move
            # Call set_value with same block to force a re-paint, I believe this
            # ultimately chains down to the 'property-notify-event' signal being
            # sent to the relevent TreeView widget, but I'm not sure how to
            # replicate just that part of the functionality
            self.board['liststore'].set_value(treeiter, coord.x, block)

    def play_move(self, move):
        self.do_move(move)

    def unplay_move(self, move):
        self.do_move(move, True)

    def main(self):
        Gtk.main()
