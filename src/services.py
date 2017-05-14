#
# Services control
#

import subprocess

SYSTEMCTL_BINPATH = '/bin/systemctl'


def start(name):
    subprocess.check_call([SYSTEMCTL_BINPATH, 'start', name])

def stop(name):
    subprocess.check_call([SYSTEMCTL_BINPATH, 'stop', name])

def restart(name):
    subprocess.check_call([SYSTEMCTL_BINPATH, 'restart', name])

def enable(name):
    subprocess.check_call([SYSTEMCTL_BINPATH, 'enable', name])

def disable(name):
    subprocess.check_call([SYSTEMCTL_BINPATH, 'disable', name])

def ls():
    elements = []
    out = subprocess.check_output([SYSTEMCTL_BINPATH, '-a', '--no-pager'])
    out = out.splitlines()
    assert len(out) > 5
    out = out[1:-7]
    for line in out:
        if line.startswith(b' '):
            name, loaded, active, sub, desc = line.split(None, 4)
        else:
            _, name, loaded, active, sub, desc = line.split(None, 5)
        elements.append((name, loaded, active, sub, desc.strip()))

    return elements



if __name__ == '__main__':
    for name, loaded, active, sub, desc in ls():
        print(name)
    restart('dnsmasq.service')
    print('done')


