# vim: ts=4 et sw=4 sts=4

import threading
from Queue import Queue

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

from common.data import Move
from common.gui import *
from common.bot import Bot

from client import Client
from Clear_client import Clear_Connection as Connection
from comm import GameServer

from bots.human_bot import HumanBot

class HumanBoardGui(BoardGui):
    def __init__(self, player_id, move_queue, *args, **kwds):
        self.player_id = player_id
        self.move_queue = move_queue
        self.BlockClassKwds.update({
            'on_enter' : self.on_block_enter,
            'on_leave' : self.on_block_leave,
            'on_button_press_event' : self.on_block_button_press_event,
            })
        super(HumanBoardGui, self).__init__(*args, **kwds)

        self.current_piece = None

    def build_piece_libraries(self):
        self.piece_library = {p : PieceLibraryGui(
                    player_id=p,
                    library=self.library,
                    restrict_piece_ids_to=self.restrict_piece_ids_to,
                    ) for p in (set(xrange(self.player_count)) - set([self.player_id]))}
        self.piece_library[self.player_id] = ClickablePieceLibraryGui(
                    player_id=self.player_id,
                    library=self.library,
                    restrict_piece_ids_to=self.restrict_piece_ids_to,
                    on_button_press_event=self.on_piece_tray_click,
                    )

    def on_piece_tray_click(self, widget, event, piece):
        if piece.clicked:
            self.current_piece = piece
            self.current_piece_rotation = 0
            self.current_piece_coords = self.current_piece.get_CCW_coords(self.current_piece_rotation)
        else:
            self.current_piece = None

    def on_block_helper(self, block, val):
        if self.current_piece is not None:
            b = self.index(block)
            for c in self.current_piece_coords:
                a = b + c
                try:
                    self[a].attempt_play_id = val
                except IndexError:
                    pass

    def on_block_enter(self, widget, event, block):
        self.on_block_helper(block, self.player_id)

    def on_block_leave(self, widget, event, block):
        self.on_block_helper(block, None)

    def on_block_button_press_event(self, widget, event, block):
        if self.current_piece is None:
            return

        # Filter double/triple click events
        if event.type != Gdk.EventType.BUTTON_PRESS:
            return

        if event.button == 1:
            move = Move(
                    player_id = self.player_id,
                    piece_id = self.current_piece.piece_id,
                    rotation = self.current_piece_rotation,
                    position = self.index(block),
                    )
            if self.is_valid_move(move):
                self.move_queue.put(move, block=False)
        elif event.button > 1:
            self.on_block_leave(widget, event, block)
            self.current_piece_rotation += 1
            self.current_piece_rotation %= 4
            self.current_piece_coords = self.current_piece.get_CCW_coords(self.current_piece_rotation)
            self.on_block_enter(widget, event, block)

    def get_status_string(self):
        s = super(HumanBoardGui, self).get_status_string()

        s += ' || '
        if self.turn == self.player_id:
            s += "It's your turn"
        else:
            s += "It's player %d's turn, waiting for move..." % (self.turn)

        return s

class HumanClient(Client):
    def build_server(self):
        default_host = self.config.get('DEFAULT', 'server_host')
        default_port = self.config.get('DEFAULT', 'server_port')

        config_grid = Gtk.Grid()

        host_label = Gtk.Label('Host server')
        host_label.set_halign(Gtk.Align.END)
        config_grid.attach(host_label, 0,0,1,1)
        host_entry = Gtk.Entry()
        host_entry.set_text(default_host)
        config_grid.attach(host_entry, 1,0,1,1)

        port_label = Gtk.Label('Port')
        port_label.set_halign(Gtk.Align.END)
        config_grid.attach(port_label, 0,1,1,1)
        port_entry = Gtk.Entry()
        port_entry.set_text(default_port)
        config_grid.attach(port_entry, 1,1,1,1)

        config_grid.set_column_spacing(5)

        cancel_button = Gtk.Button(stock=Gtk.STOCK_CANCEL, use_stock=True)
        cancel_button.connect('clicked', self.build_server_destroy)

        connect_button = Gtk.Button(stock=Gtk.STOCK_CONNECT, use_stock=True)
        connect_button.connect('clicked', self.on_connect, host_entry, port_entry)

        button_line = Gtk.HBox()
        button_line.pack_start(cancel_button, True, False, 0)
        button_line.pack_end(connect_button, True, False, 0)

        vbox = Gtk.VBox()
        vbox.add(config_grid)
        vbox.add(button_line)

        server_window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        server_window.add(vbox)
        server_window.connect('destroy', self.build_server_destroy)
        server_window.connect('key-press-event', self.build_server_keypress)

        server_window.show_all()

        connect_button.grab_focus()

        self.server = None
        while self.server is None:
            Gtk.main()

        server_window.destroy()
        while Gtk.events_pending():
            Gtk.main_iteration()

    def __init__(self, *args, **kwds):
        self.move_queue = Queue()

        GObject.threads_init()
        Gdk.threads_init()
        Gdk.threads_enter()
        super(HumanClient, self).__init__(*args, **kwds)
        Gdk.threads_leave()

    def on_connect(self, widget, host_entry, port_entry):
        server = (host_entry.get_text(), int(port_entry.get_text()))
        try:
            # XXX: Get I/O off the main thread somehow
            self.server = GameServer(connection=Connection(server))
        except Exception as e:
            dialog = Gtk.Dialog(
                    title="Game Server Connection Error",
                    flags=Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    buttons=(Gtk.STOCK_CLOSE,Gtk.ResponseType.CLOSE),
                    )
            ca = dialog.get_content_area()
            l = Gtk.Label(str(e))
            l.set_line_wrap_mode(True)
            ca.add(l)
            ca.show_all()
            dialog.run()
            dialog.destroy()

        Gtk.main_quit()

    def build_server_keypress(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.build_server_destroy(widget)

    def build_server_destroy(self, widget, data=None):
        if self.server is None:
            sys.exit()

    def board_builder(self, **kwds):
        return HumanBoardGui(player_id=self.server.player_id, move_queue=self.move_queue, **kwds)

    class GameLoop(threading.Thread):
        def __init__(self, game_server, bot, **kwds):
            self.game_server = game_server
            self.bot = bot
            super(HumanClient.GameLoop, self).__init__(**kwds)

        def run(self):
            while self.game_server.game_loop(self.bot):
                pass

    def play_game(self):
        Gdk.threads_enter()
        player_id, board = self.server.join_game(board_constructor=self.board_builder)
        self.bot = HumanBot(player_id=player_id, board=board, move_queue=self.move_queue)
        Gdk.threads_leave()

        self.loop_thread = self.GameLoop(self.server, self.bot)
        self.loop_thread.daemon = True
        self.loop_thread.start()

        Gdk.threads_enter()
        Gtk.main()
        Gdk.threads_leave()

if __name__ == '__main__':
    # XXX: Write unit tests?
    HumanClient().play_game()
