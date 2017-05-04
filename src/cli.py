import argparse

import config
from tests.classification import ClassificationCorrectnessTest, ClassificationTimeTest


class TestModes(object):
    """Test mode namespace."""
    CORRECTNESS = 'correctness'
    TIME = 'time'

    ALL = [CORRECTNESS, TIME]


# Subcommands


def classification_sub(args):
    """:rtype : int"""
    {
        TestModes.CORRECTNESS: ClassificationCorrectnessTest(),
        TestModes.TIME: ClassificationTimeTest()
    }[args.mode].start()
    return 0


# CLI parser


def build_parser():
    """Build and return the CLI parser.

    :rtype : argparse.ArgumentParser
    """
    # Help parser
    help_parser = argparse.ArgumentParser(add_help=False)

    group = help_parser.add_argument_group('Help and debug')
    group.add_argument('--debug',
                       help='Enable debug output.',
                       action=_EnableDebugAction)
    group.add_argument('-h', '--help',
                       help='Show this help message and exit.',
                       action='help')

    # Mode parser
    mode_parser = argparse.ArgumentParser(add_help=False)

    group = mode_parser.add_argument_group('Mode')
    group.add_argument('-m', '--mode',
                       choices=TestModes.ALL,
                       default=TestModes.ALL[0],
                       help='Test mode.')

    # Main parser
    main_parser = argparse.ArgumentParser(prog='test',
                                          description='Test suite for the MiniME reasoner.',
                                          parents=[help_parser],
                                          add_help=False)

    subparsers = main_parser.add_subparsers(title='Available tests')

    # Classification subcommand
    desc = 'Perform the classification test.'
    parser_classification = subparsers.add_parser('classification',
                                                  description=desc,
                                                  help=desc,
                                                  parents=[help_parser, mode_parser],
                                                  add_help=False)

    parser_classification.set_defaults(func=classification_sub)

    return main_parser


# Private classes


# noinspection PyProtectedMember
class _EnableDebugAction(argparse._StoreTrueAction):
    """Argparse action to enable debug output."""

    def __call__(self, parser, namespace, values, option_string=None):
        debug = self.const
        if debug:
            config.debug = True  # Respect cli argument.
        else:
            self.const = config.debug  # Set cli argument to config value.
        super(_EnableDebugAction, self).__call__(parser, namespace, values, option_string)
