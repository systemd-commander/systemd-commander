#
#
#

from configparser import SafeConfigParser
import os.path

import urwid

import services
import machines
import journal

CONF_FNAMES = (
    '/etc/systemd-commander.conf',
    '~/.config/systemd-commander.conf',
    '~/.systemd-commander.conf'
)


# Keypress callbacks


def show_help(data):
    return


def do_nothing(data):
    return


def do_exit(data):
    raise urwid.ExitMainLoop()


func_keys = {
    'F1': ('Blah', do_nothing),
    'F2': ('Blah', do_nothing),
    'F3': ('Blah', do_nothing),
    'F4': ('Blah', do_nothing),
    'F5': ('Blah', do_nothing),
    'F6': ('Blah', do_nothing),
    'F7': ('Blah', do_nothing),
    'F8': ('Blah', do_nothing),
    'F9': ('Blah', do_nothing),
    'F10': ('Exit', do_exit),
}


class SystemdCommander:

    def __init__(self):
        self.header = None
        self.conf = {}
        self.load_config()
        self._commanders = (
            services.ServiceCommander(),
            journal.JournaldCommander(),
            machines.MachinedCommander(),
            machines.ImageCommander(),
        )
        self._tab_names = ('Help', 'Services', 'Journal', 'Machines', 'Images')
        self._selected_tab = 'Services'

    def handle_tab_select(self, key):
        index = int(key[1:]) - 1
        try:
            self._selected_tab = self._tab_names[index]
        except IndexError:
            return
        header = ''
        for name in self._tab_names:
            if name == self._selected_tab:
                header += "[%s]" % name
            else:
                header += " %s " % name
        self.header.set_text(header)

        # pick commander, call list generator
        self.selected_items = set()
        i = self._tab_names.index(self._selected_tab)
        c = self._commanders[i - 1]
        elements = c.get_list()
        names = []
        for e in elements:
            if isinstance(e, list):
                names.append(e[0])
            elif isinstance(e, str):
                names.append(e)
            elif isinstance(e, bytes):
                names.append(e)
            else:
                names.append(repr(e))
        self.update_selector_box(names)

    def handle_selector_box_enter(self, item):
        if not item.selectable():
            return
        if hasattr(item, 'unselected_label'):
            # ugly!
            item.set_label(item.unselected_label)
            self.selected_items.discard(item.unselected_label)
            del(item.unselected_label)
        else:
            item.unselected_label = item.label
            self.selected_items.add(item.label)
            item.set_label(b'* ' +item.label)

    def update_selector_box(self, names):
        new_items = []
        for name in names:
            w = urwid.AttrMap(
                urwid.Button(
                    name,
                    on_press=self.handle_selector_box_enter,
                ),
                'bg'
            )
            w.rows((2,))
            new_items.append(w)
        self.selector_box_items[:] = new_items

    def load_config(self):
        cp = SafeConfigParser()
        conf_fnames = [os.path.expanduser(fn) for fn in CONF_FNAMES]
        cp.read(conf_fnames)
        for s in cp.sections():  # FIXME filter valid sections
            self.conf[s] = {}
            for name, val in cp.items():
                self.conf[s][name] = val

    def handle_input(self, key):
        if type(key) != str:
            # could be a mouse event, e.g. ('mouse press', button, x, y)
            return None
        if key.lower() in ('q', 'esc'):
            raise urwid.ExitMainLoop()
        if key.upper() in func_keys:
            self.handle_tab_select(key.upper())
            return

    def build_ui(self):
        palette = (
            ('bg', 'white', 'black'),
        )
        screen = urwid.raw_display.Screen()
        self.show_box = urwid.ListBox([urwid.Text('show box')])
        self.selector_box_items = urwid.SimpleFocusListWalker([])
        self.header = urwid.Text(('bold', u""), 'left', 'clip')
        container = urwid.Pile([
            (1, urwid.Filler(self.header, 'top')),
            urwid.Columns([
                urwid.LineBox(
                    urwid.ListBox(
                        self.selector_box_items
                    )
                ),
                urwid.LineBox(self.show_box),
            ])
        ])

        self.handle_tab_select('F2')
        urwid.MainLoop(container, palette, screen=screen,
                       unhandled_input=self.handle_input).run()


def main():
    sc = SystemdCommander()
    sc.build_ui()


if __name__ == '__main__':
    main()
