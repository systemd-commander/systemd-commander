#
# Journald interface
#

from systemd import journal


class JournalCommander():
    def __init__(self):
        self._cursors = {}  # unit -> position
        self._selected_unit_names = set()

    def create_reader(self, level=journal.LOG_DEBUG):
        j = journal.Reader()
        j.log_level(journal.LOG_INFO)
        for unit_name in self._selected_unit_names:
            j.add_match(_SYSTEMD_UNIT=unit_name)
        return j
