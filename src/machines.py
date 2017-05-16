#
# Machined interface
#

import subprocess
import utils
from utils import parse_table


class MachinedCommander():
    """Interface to Machined. Manage VMs and containers.<F2>
    """
    def __init__(self):
        self._binpath = '/bin/machinectl'

    def start_machine(self, name):
        subprocess.check_call([self._binpath, 'start', name])

    def stop_machine(self, name):
        subprocess.check_call([self._binpath, 'stop', name])

    def get_list(self):
        out = subprocess.check_output([self._binpath, 'list'])
        return parse_table(out)

    def pull_raw_image(self, name, verify=True):
        if verify:
            subprocess.check_call([self._binpath, 'pull-raw', name])
        else:
            subprocess.check_call([self._binpath, 'pull-raw', '--verify=no',
                                   name])


class ImageCommander():

    def get_list(self):
        li = utils.runcmd('machinectl', ['list-images'])
        return [i['NAME'] for i in li]


if __name__ == '__main__':
    from time import sleep
    c = MachinedCommander()
    print("Machines")
    print(c.list_machines())
    assert c.list_machines() == []
    print("Images")
    img = c.list_images()
    print(img)
    assert len(img) > 0
    img_name = img[0]['NAME']
    print("Staring VM")
    c.start_machine(img_name)
    sleep(5)
    m = c.list_machines()
    print(m)
    assert len(m) > 0
    print("Stopping VM")
    c.stop_machine(img_name)
    sleep(5)
    m = c.list_machines()
    print(m)
    assert m == 0
