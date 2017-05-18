#
# Services control
#

import utils


class ServiceCommander():
    name = 'Services'
    allow_multiple_selection = False

    def __init__(self):
        pass

    def start(self, name):
        utils.runcmd('systemctl', ['start', name])

    def stop(self, name):
        utils.runcmd('systemctl', ['stop', name])

    def restart(self, name):
        utils.runcmd('systemctl', ['restart', name])

    def enable(self, name):
        utils.runcmd('systemctl', ['enable', name])

    def disable(self, name):
        utils.runcmd('systemctl', ['disable', name])

    def get_list(self):
        li = utils.runcmd('systemctl', ['--all', '--no-pager'])
        return [i['UNIT'].replace(b'\x8f ', b'') for i in li]

    def handle_key(self, main, keymap, key, selected):
        cmd = keymap[key]
        if cmd == 'restart':
            for s in selected:
                main.set_status("Restarting {}...".format(s))
                self.restart(s)

if __name__ == '__main__':
    c = ServiceCommander()
    # c.restart('dnsmasq.service')
    print([i['UNIT'] for i in c.get_list()])
    print()
    print([i['SUB'] for i in c.get_list()])
    print()
    print([i['ACTIVE'] for i in c.get_list()])
    print('done')
