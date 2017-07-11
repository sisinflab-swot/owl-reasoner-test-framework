import errno

import exc
import proc


def detect_connected():
    """Returns the name of a connected device."""
    args = [proc.find_executable('instruments'), '-s', 'devices']
    output = proc.call(args).stdout

    for line in output.splitlines():
        components = line.split(' (', 1)

        if len(components) == 2 and not components[1].endswith('(Simulator)'):
            return components[0]

    exc.raise_ioerror(errno.ENODEV, message='No connected devices.')
