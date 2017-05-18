#
# Journald interface
#

import subprocess
from systemd import journal

import utils


class JournaldCommander():
    name = 'Journal'
    allow_multiple_selection = True

    def __init__(self):
        self._cursors = {}  # unit -> position
        self._selected_unit_names = set()

    def create_reader(self, level=journal.LOG_DEBUG):
        j = journal.Reader()
        j.log_level(journal.LOG_INFO)
        for unit_name in self._selected_unit_names:
            j.add_match(_SYSTEMD_UNIT=unit_name)
        return j

    def get_list(self):
        """List unit files"""
        li = utils.runcmd('systemctl', ['list-unit-files', '--all',
                                          '--no-pager'])
        return [i['UNIT FILE'] for i in li]

    def handle_key(self, main, keymap, key, selected):
        pass
