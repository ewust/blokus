# vim: ts=4 et sw=4 sts=4

# TTTA: Can a gui board subclass from a regular board, perhaps replacing the
# underlying Block class to allow for re-drawing? Things are starting to
# duplicate a lot

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

from common.data import Block,Board,Piece,PieceFactory

__version__ = 0.1

class BlockGui(Block):
    pixbufs = {
            'alpha' : GdkPixbuf.Pixbuf.new_from_file('common/resources/block_alpha.png'),
            'empty' : GdkPixbuf.Pixbuf.new_from_file('common/resources/block_empty.png'),
            'blue' : GdkPixbuf.Pixbuf.new_from_file('common/resources/block_blue.png'),
            'yellow' : GdkPixbuf.Pixbuf.new_from_file('common/resources/block_yellow.png'),
            'red' : GdkPixbuf.Pixbuf.new_from_file('common/resources/block_red.png'),
            'green' : GdkPixbuf.Pixbuf.new_from_file('common/resources/block_green.png'),
            }

    id_to_color = {
            0 : 'blue',
            1 : 'yellow',
            2 : 'red',
            3 : 'green',
            }

    def __init__(self, color=None, player_id=None, **kwds):
        super(BlockGui, self).__init__(**kwds)

        if player_id is not None:
            if player_id not in BlockGui.id_to_color.keys():
                raise TypeError, "Player ID must be one of: " + str(BlockGui.id_to_color.keys())
        self.player_id = player_id
        if color is not None:
            if color not in BlockGui.pixbufs.keys():
                raise TypeError, "Color must be one of: " + str(BlockGui.pixbufs.keys())
        self.color = color

    def get_pixbuf(self):
        if self.player_id is not None:
            return BlockGui.pixbufs[BlockGui.id_to_color[self.player_id]]
        if self.color is not None:
            return BlockGui.pixbufs[self.color]
        try:
            return BlockGui.pixbufs[BlockGui.id_to_color[self.move.player_id]]
        except AttributeError:
            return BlockGui.pixbufs['empty']

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

class PieceGui(Piece):
    def build_treeview(self):
        fmt = []
        for c in xrange(self.shape[0]):
            fmt.append(GObject.TYPE_PYOBJECT)
        liststore = Gtk.ListStore(*fmt)

        for y in xrange(self.min_y, self.max_y+1):
            row = []
            for x in xrange(self.min_x, self.max_x+1):
                if (x,y) in self.coords:
                    row.append(BlockGui(player_id=self.player_id, color='empty'))
                else:
                    row.append(BlockGui(color='alpha'))
            liststore.append(row)

        treeview = Gtk.TreeView(liststore)

        for col in xrange(self.shape[0]):
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
        g = treeview.get_grid_lines()
        treeview.set_grid_lines(g.NONE)

        treeview.set_hexpand(True)
        treeview.set_vexpand(True)
        treeview.set_halign(Gtk.Align.CENTER)
        treeview.set_valign(Gtk.Align.FILL)

        treeview.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0,0,0,0))

        treeview.get_selection().set_mode(Gtk.SelectionMode.NONE)

        self.treeview = treeview

        piece_box = Gtk.VBox()
        piece_box.add(Gtk.HSeparator())
        piece_box.add(Gtk.HSeparator())
        piece_box.add(self.treeview)

        self.boxed_and_sep_treeview = piece_box

    def __init__(self, player_id=None, **kwds):
        super(PieceGui, self).__init__(**kwds)

        self.player_id = player_id
        self.build_treeview()

class PieceFactoryGui(PieceFactory):
    def _build_piece(self, piece_id, from_str):
        return PieceGui(player_id=self.player_id, piece_id=piece_id, from_str=from_str)

    def __init__(self, player_id=None, **kwds):
        self.player_id = player_id
        super(PieceFactoryGui, self).__init__(**kwds)

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

        treeview.set_halign(Gtk.Align.CENTER)
        treeview.set_valign(Gtk.Align.CENTER)

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

    def build_piece_factory(self, library):
        self.piece_factory = PieceFactory(library)

        self.piece_trays = {}
        for p in xrange(self.player_count):
            self.piece_trays[p] = PieceFactoryGui(player_id=p, library=library)

    def build_piece_tray_box(self, player_id):
        vbox = Gtk.Grid()
        vbox.set_row_homogeneous(False)
        vbox.set_orientation(Gtk.Orientation.VERTICAL)

        vbox.add(Gtk.Label('Player %d Tray' % (player_id)))

        scrolled_box = Gtk.Grid()
        scrolled_box.set_row_homogeneous(False)
        scrolled_box.set_orientation(Gtk.Orientation.VERTICAL)
        scrolled_box.set_hexpand(True)
        scrolled_box.set_vexpand(True)
        scrolled_box.set_halign(Gtk.Align.FILL)
        scrolled_box.set_valign(Gtk.Align.FILL)
        for piece in self.piece_trays[player_id]:
            scrolled_box.add(piece.boxed_and_sep_treeview)
        sep = Gtk.Separator()
        sep.set_orientation(Gtk.Orientation.HORIZONTAL)
        scrolled_box.add(sep)
        sep = Gtk.Separator()
        sep.set_orientation(Gtk.Orientation.HORIZONTAL)
        scrolled_box.add(sep)

        scrolled = Gtk.ScrolledWindow()
        scrolled.add_with_viewport(scrolled_box)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vbox.add(scrolled)

        self.piece_tray_scrolled_boxes[player_id] = scrolled_box
        self.piece_tray_boxes[player_id] = vbox

    def get_top_level_box(self):
        return self.board_and_trays_box

    def __init__(self, **kwds):
        super(BoardGui, self).__init__(**kwds)

        self.move_history = []
        self.current_move = -1

        self.build_board_area_box()
        self.piece_tray_scrolled_boxes = {}
        self.piece_tray_boxes = {}
        for p in xrange(self.player_count):
            self.build_piece_tray_box(p)

        self.board_and_trays_box = Gtk.HBox()
        self.board_and_trays_box.add(self.board_area_box)
        for p in xrange(self.player_count):
            self.board_and_trays_box.add(Gtk.VSeparator())
            self.board_and_trays_box.add(self.piece_tray_boxes[p])
        self.board_and_trays_box.add(Gtk.VSeparator())

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

    def piece_tray_activate(self, player_id):
        pass

    def piece_tray_deactivate(self, player_id):
        pass

    def piece_tray_add(self, player_id, piece_id):
        self.piece_tray_scrolled_boxes[player_id].add(self.piece_trays[player_id][piece_id].boxed_and_sep_treeview)

    def piece_tray_remove(self, player_id, piece_id):
        self.piece_tray_scrolled_boxes[player_id].remove(self.piece_trays[player_id][piece_id].boxed_and_sep_treeview)

    def do_move(self, move, unplay=False):
        if move.is_skip():
            if move.is_voluntary_skip():
                if unplay:
                    self.piece_tray_activate(move.player_id)
                else:
                    self.piece_tray_deactivate(move.player_id)
            return

        if unplay:
            self.piece_tray_add(move.player_id, move.piece_id)
        else:
            self.piece_tray_remove(move.player_id, move.piece_id)

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
