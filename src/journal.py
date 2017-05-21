#
# Journald interface
#

from systemd import journal
from threading import Thread
from time import sleep

import utils


class JournaldCommander():
    name = 'Journal'
    allow_multiple_selection = True

    def __init__(self):
        self._cursors = {}  # unit -> position
        self._selected_unit_names = set()
        self._follower = None

    def create_reader(self, level=journal.LOG_DEBUG):
        j = journal.Reader()
        j.log_level(journal.LOG_INFO)
        self._selected_unit_names = self.main.selected_items
        if self._selected_unit_names:
            for unit_name in self._selected_unit_names:
                j.add_match(_SYSTEMD_UNIT=unit_name)
        return j

    def get_list(self):
        """List unit files"""
        li = utils.runcmd('systemctl', ['list-unit-files', '--all',
                                        '--no-pager'])
        return [i['UNIT FILE'] for i in li]

    def handle_key(self, main, keymap, key, selected):
        cmd = keymap[key]
        self.main.set_status(cmd)
        if cmd == 'toggle_follow':
            if self._follower is None or self._follower.stopping:
                r = self.create_reader()
                self._follower = Follower(self.main, r)
                self._follower.start()
                ul = len(self._selected_unit_names) or "all"
                main.set_status("Following {} units...".format(ul))
            else:
                self._follower.stopping = True
                main.set_status("Stop following...")


class Follower(Thread):
    stopping = False

    def __init__(self, main, reader):
        self.main = main
        self.reader = reader
        super(Follower, self).__init__()

    def run(self):
        self.reader.seek_tail()
        while not self.stopping:
            l = None
            while True:
                nl = self.reader.get_next()
                if nl == {}:
                    break
                l = nl
            if l is not None:
                i = "{} {}".format(l['__REALTIME_TIMESTAMP'], l['MESSAGE'])
                self.main.append_to_show_box(i)
                self.main.mainloop.draw_screen()
            sleep(.2)

    def stop(self):
        self.stopping = True
