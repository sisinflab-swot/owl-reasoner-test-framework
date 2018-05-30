import sys

from . import cli, config
from .pyutils import echo


# Main


def main() -> int:
    try:
        parser = cli.build_parser()
        args = parser.parse_args()

        if args.debug:
            config.DEBUG = True

        if not hasattr(args, 'func'):
            raise ValueError('Invalid argument(s). Please run "test -h" or "test <subcommand> -h" for help.')

        ret_val = args.func(args)
    except KeyboardInterrupt:
        echo.error('Interrupted by user.')
        ret_val = 1
    except Exception as e:
        if config.DEBUG:
            raise
        else:
            echo.error(str(e))
            ret_val = 1

    return ret_val


if __name__ == '__main__':
    sys.exit(main())
