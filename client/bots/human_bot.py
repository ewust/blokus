# vim: ts=4 et sw=4 sts=4

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk,GObject

from common.bot import SimpleStatusHandler,PlayOnReport,Bot
from common.gui import BoardGui

class HumanBot(SimpleStatusHandler, PlayOnReport, Bot):
    def __init__(self, move_queue, **kwds):
        self.move_queue = move_queue
        super(HumanBot, self).__init__(**kwds)

    def get_move(self):
        return self.move_queue.get()

    def report_move(self, move):
        GObject.idle_add(self.real_report_move, move)

    def report_status(self, status_code, message):
        GObject.idle_add(self.real_report_status, status_code, message)

    def real_report_move(self, move):
        super(HumanBot, self).report_move(move)
        self.board.update_labels()

    def real_report_status(self, status_code, message):
        super(HumanBot, self).report_status(status_code, message)
        self.board.update_labels()
