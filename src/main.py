#
#
#

from configparser import SafeConfigParser
import os.path
from threading import Thread
import time

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


class SystemdCommander:

    def __init__(self):
        self.header = None
        self.inputting_search = False
        self.conf = {}
        self.load_config()
        self._commanders = (
            services.ServiceCommander(),
            journal.JournaldCommander(),
            machines.MachinedCommander(),
            machines.ImageCommander(),
        )
        for c in self._commanders:
            c.main = self
        self._tab_names = (
            'F1 Help', 'F2 Services', 'F3 Journal',
            'F4 Machines', 'F5 Images')
        self._selected_tab = self._tab_names[1]
        self.status_update_time = time.time()

    @property
    def current_commander(self):
        # ugly
        i = self._tab_names.index(self._selected_tab)
        return self._commanders[i - 1]

    def handle_tab_select(self, key):
        """Switch to the selected tab (if existing),
        update the selector list content
        """
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
        self.header.original_widget.set_text(header)

        # pick commander, call list generator
        self.selected_items = set()
        elements = self.current_commander.get_list()
        names = []
        for e in elements:
            # TODO: cleanup
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
        """Handle space or enter on a selector item
        """
        if self.inputting_search:
            self.search_in_show_box('\n')
        if not self.current_commander.allow_multiple_selection:
            return
        if not item.selectable():  # TODO: needed?
            return
        if hasattr(item, 'unselected_label'):
            # ugly!
            item.set_label(item.unselected_label)
            self.selected_items.discard(item.unselected_label)
            del(item.unselected_label)
        else:
            item.unselected_label = item.label
            self.selected_items.add(item.label)
            item.set_label(b'* ' + item.label)

    def update_selector_box(self, names):
        new_items = []
        self.selector_box_buttons = []
        for name in names:
            b = urwid.Button(
                name,
                on_press=self.handle_selector_box_enter,
            )
            self.selector_box_buttons.append(b)
            w = urwid.AttrMap(
                b,
                None,
                'selected',
            )
            b._parent = w
            w.rows((2,))
            new_items.append(w)
        self.selector_box_items[:] = new_items

    def load_config(self):
        cp = SafeConfigParser()
        conf_fnames = [os.path.expanduser(fn) for fn in CONF_FNAMES]
        cp.read(conf_fnames)
        for s in cp.sections():  # FIXME filter valid sections
            self.conf[s] = {}
            for name, val in cp[s].items():
                self.conf[s][name] = val

    def handle_input(self, key):
        if type(key) != str:
            # could be a mouse event, e.g. ('mouse press', button, x, y)
            return None
        if key.upper()[0] == 'F' and len(key) > 1:
            self.inputting_search = False
            self.handle_tab_select(key.upper())
            return
        if key == 'esc':
            raise urwid.ExitMainLoop()
        if self.inputting_search:
            self.search_in_show_box(key)
            return
        if key == 'q':
            raise urwid.ExitMainLoop()
        for cmd, v in self.conf["global:keys"].items():
            if key == v:
                if cmd == 'search':
                    self.inputting_search = True
                    self.search_in_show_box(None)
                return

        # pass key to the selected commander
        keyconf = self.conf["%s:keys" % self.current_commander.name]
        keymap = {v: k for k, v in keyconf.items()}
        keyconf = self.conf["global:keys"]
        for k, v in keyconf.items():
            keymap[v] = k
        if key not in keymap:
            self.set_status("Unknown key '{}'".format(key))
            return

        self.current_commander.handle_key(
            self,
            keymap,
            key,
            self.selected_items,
        )

    def handle_selector_change(self):
        index = str(self.selector_box.get_focus()[1])
        self.set_status(index)

    def append_to_show_box(self, x):
        w = urwid.AttrMap(urwid.Text(x))
        self.show_box_items.append(w)

    def search_in_show_box(self, s):
        """Receive search string one char at a time starting
        with a None
        """
        if s == None:
            self.search_string = ''
        elif s == '\n':
            self.inputting_search = False
            return
        elif s == 'backspace':
            if s != '':
                self.search_string = self.search_string[:-1]
        else:
            # TODO handle other special char
            self.search_string += s

        self.set_status("/" + self.search_string)
        for i in self.selector_box_buttons:
            if self.search_string in i.get_label().decode('utf-8'):
                #self.set_status(i.get_label().decode('utf-8'))
                #i._parent.set_attr_map(selected)
                pass


    def build_ui(self):
        g = self.conf['global']
        palette = (
            (None, g['foreground_color'], g['background_color']),
            ('selected', 'black', 'white')
        )
        screen = urwid.raw_display.Screen()
        self.show_box_items = urwid.SimpleFocusListWalker([])
        self.show_box = urwid.ListBox(self.show_box_items)
        self.selector_box_items = urwid.SimpleFocusListWalker([])
        self.selector_box = urwid.ListBox(self.selector_box_items)

        self.header = urwid.AttrMap(
            urwid.Text(('bold', u""), 'left', 'clip'),
            'palette',
        )
        self.footer = urwid.Text(('bold', u""), 'left', 'clip')
        container = urwid.Pile([
            (1, urwid.Filler(self.header, 'top')),
            urwid.Columns([
                urwid.LineBox(
                    self.selector_box
                ),
                urwid.LineBox(self.show_box),
            ]),
            (1, urwid.Filler(self.footer, 'top')),
        ])

        self.handle_tab_select('F2')

        urwid.connect_signal(self.selector_box_items, "modified",
                             self.handle_selector_change)
        self.mainloop = urwid.MainLoop(container, palette, screen=screen,
                                       unhandled_input=self.handle_input)
        self.mainloop.run()

    def set_status(self, msg):
        self.footer.set_text(" " + msg)
        self.status_update_time = time.time()


def reset_status(main):
    while True:
        if main.status_update_time < time.time() - 0.5:
            main.set_status('')
            main.mainloop.draw_screen()

        time.sleep(.1)


def main():
    sc = SystemdCommander()
    refresh = Thread(target=reset_status, args=(sc, ))
    refresh.start()
    sc.build_ui()


if __name__ == '__main__':
    main()
