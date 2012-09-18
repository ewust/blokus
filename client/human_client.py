# vim: ts=4 et sw=4 sts=4

import sys
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from common.gui import BoardGui
from common.bot import Bot

from client import Client
from Clear_client import Clear_Connection as Connection
from comm import GameServer

from bots.human_bot import HumanBot

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
        GObject.threads_init()
        super(HumanClient, self).__init__(*args, **kwds)

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

    class GameLoop(threading.Thread):
        kill_event = threading.Event()

        def run(self):
            while not self.kill_event.isSet():
                while self.server.game_loop(self.bot):
                    pass

        def stop(self):
            self.kill_event.set()

    def play_game(self):
        player_id, board = self.server.join_game(BoardGui)
        self.bot = HumanBot(player_id=player_id, board=board)
        self.loop_thread = self.GameLoop()
        self.loop_thread.start()
        Gtk.main()

if __name__ == '__main__':
    # XXX: Write unit tests?
    HumanClient().play_game()
