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
        def sq(size):
            return gtk.gdk.Rectangle(width=size, height=size)

        fmt = []
        for c in xrange(self.cols):
            fmt.append(gtk.gdk.Pixbuf)
        liststore = gtk.ListStore(*fmt)

        tv_cols = []
        for c in xrange(self.cols):
            tv_cols.append(gtk.TreeViewColumn(str(c)))

        self.blocks = {
                'empty' : gtk.gdk.pixbuf_new_from_file('resources/block_empty.png'),
                'red' : gtk.gdk.pixbuf_new_from_file('resources/block_red.png'),
                'blue' : gtk.gdk.pixbuf_new_from_file('resources/block_blue.png'),
                'green' : gtk.gdk.pixbuf_new_from_file('resources/block_green.png'),
                'yellow' : gtk.gdk.pixbuf_new_from_file('resources/block_yellow.png'),
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
