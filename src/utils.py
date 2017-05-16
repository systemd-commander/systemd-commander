#
# Utils
#

import subprocess

BIN_PATHS = {
    'systemctl': '/bin/systemctl',
    'machinectl': '/bin/machinectl',
}


def parse_table(text):
    """Parse tabular output
    """
    headers = None
    elements = []
    for line in text.splitlines():
        if headers is None:
            headers = []
            if line != line.upper():
                return []  # no header found, empty table
            prev_char = ' '
            prev_prev_char = ' '
            current_header_pos = None
            current_header = ''
            for i, c in enumerate(line):
                c = chr(c)
                if c != ' ' and prev_char == ' ' and prev_prev_char == ' ':
                    # starting of new header
                    if current_header_pos is not None:
                        # save previous header
                        headers.append((current_header_pos,
                                        current_header.rstrip()))

                    current_header_pos = i
                    current_header = c
                    prev_prev_char = prev_char
                    prev_char = c
                    continue

                # continuing header
                current_header += c
                prev_prev_char = prev_char
                prev_char = c

            # save last header
            headers.append((current_header_pos, current_header.rstrip()))
            continue  # table header parsed

        # parsing a table row
        if line == b'':
            break  # ignore "footer" lines
        e = {}
        for (i1, h1), (i2, h2) in zip(headers, headers[1:]):
            field = line[i1:i2].rstrip()
            e[h1] = field
        # last cell
        field = line[i2:].rstrip()
        e[h2] = field
        elements.append(e)

    return elements


def runcmd(nick, args):
    cmd = [BIN_PATHS[nick]]
    cmd.extend(args)
    out = subprocess.check_output(cmd)
    return parse_table(out)
