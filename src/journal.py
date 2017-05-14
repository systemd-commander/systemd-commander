#
# Journald interface
#

from systemd import journal


def create_reader(level=journal.LOG_DEBUG, unit=None):
    j = journal.Reader()
    j.log_level(journal.LOG_INFO)
    if unit is not None:
        j.add_match(_SYSTEMD_UNIT=unit)
    return j


