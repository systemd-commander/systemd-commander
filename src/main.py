import urwid

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

def main():
    palette = (
        ('bg', 'white', 'black'),
    )
    screen = urwid.raw_display.Screen()
    inner_box = urwid.ListBox([urwid.Text('main box')])
    func_widgets = []
    for d in range(1, 11):
        key = 'F{}'.format(d)
        label = '{} - {}'.format(key, func_keys[key][0])
        w = urwid.AttrMap(
            urwid.Button(
                label,
                on_press=func_keys[key][0],
            ),
        'bg')
        w.rows((2,))
        func_widgets.append(w)
    command_box = urwid.GridFlow(
        func_widgets,
        cell_width=10,
        h_sep=0,
        v_sep=0,
        align='center',
    )
    command_box = urwid.ListBox(func_widgets)
    container = urwid.Pile([
        urwid.LineBox(inner_box),
        urwid.LineBox(command_box),
    ])

    def unhandled_input(key):
        if key.lower() in ('q', 'esc'):
            raise urwid.ExitMainLoop()
        if key.upper() in func_keys:
            func_keys[key.upper()][1](None)

    urwid.MainLoop(container, palette, screen=screen, unhandled_input=unhandled_input).run()


if __name__ == '__main__':
    main()
