import sys

import cli
import config
from utils import echo


# Main


def main():
    """:rtype : int"""
    parser = cli.build_parser()
    args = parser.parse_args()
    return args.func(args)


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
