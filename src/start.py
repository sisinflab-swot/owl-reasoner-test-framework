import sys

import config
from tests import classification
from utils import echo


# Main


def main():
    """:rtype : int"""
    classification.correctness()
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        echo.error('Interrupted by user.')
        sys.exit(1)
    except Exception as e:
        if config.debug:
            raise
        else:
            err_msg = e.message if e.message else str(e)
            echo.error(err_msg)
            sys.exit(1)
