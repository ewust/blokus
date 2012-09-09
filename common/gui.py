# vim: ts=4 et sw=4 sts=4

import pygtk
pygtk.require('2.0')
import gtk

__version__ = 0.1

class BlockusBoard:
    def build_menu_line(self):
        self.menu_line_elements = []

        title_string = gtk.Label("Blockus Viewer v" + str(__version__))
        self.menu_line_elements.append(title_string)

        first = gtk.Button(stock=gtk.STOCK_GOTO_FIRST)
        self.menu_line_elements.append(first)

        back = gtk.Button(stock=gtk.STOCK_GO_BACK)
        self.menu_line_elements.append(back)

        forward = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        self.menu_line_elements.append(forward)

        last = gtk.Button(stock=gtk.STOCK_GOTO_LAST)
        self.menu_line_elements.append(last)

        self.turn_id = gtk.Label("Turn 0 / ?")
        self.menu_line_elements.append(self.turn_id)

        for e in self.menu_line_elements:
            self.menu_line.pack_start(e)

    def build_board(self):
        self.board['boxes'] = []

        table = gtk.Table(self.rows, self.cols, True)
        self.board['table'] = table
        self.board['container'].pack_start(table)

        for r in xrange(self.rows):
            self.board['boxes'].append([])
            for c in xrange(self.cols):
                box = gtk.Button(label='('+str(r)+','+str(c)+')')
                table.attach(box, r, r+1, c, c+1)
                self.board['boxes'][r].append(box)

    def build_status_line(self):
        self.status_line_elements = []

        self.status_string = gtk.Label("Waiting for new moves...")
        self.status_line_elements.append(self.status_string)

        for e in self.status_line_elements:
            self.status_line.pack_start(e)

    def __init__(self, rows, cols):
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

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

if __name__ == '__main__':
    b = BlockusBoard(20, 20)
    #b = BlockusBoard(4, 4)
    b.main()
