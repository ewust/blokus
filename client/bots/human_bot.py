# vim: ts=4 et sw=4 sts=4

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk

from common.bot import SimpleStatusHandler,Bot
from common.gui import BoardGui

class HumanBot(SimpleStatusHandler, Bot):
    def get_move(self):
        Gdk.threads_enter()
        super(HumanBot, self).get_move()
        Gdk.threads_leave()

    def report_move(self):
        Gdk.threads_enter()
        super(HumanBot, self).report_move()
        Gdk.threads_leave()

    def report_status(self):
        Gdk.threads_enter()
        super(HumanBot, self).report_status()
        Gdk.threads_leave()
