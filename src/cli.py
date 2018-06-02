import argparse

from . import config
from .config import Reasoners
from .reasoners.owl import TestMode

from .tests.test import NotImplementedTest
from .tests.info import InfoTest

from .tests.abduction_contraction import (
    AbductionContractionTimeTest,
    AbductionContractionMemoryTest,
    AbductionContractionMobileTest
)

from .tests.classification import (
    ClassificationCorrectnessTest,
    ClassificationTimeTest,
    ClassificationMemoryTest,
    ClassificationMobileTest
)

from .tests.consistency import (
    ConsistencyCorrectnessTest,
    ConsistencyTimeTest,
    ConsistencyMemoryTest,
    ConsistencyMobileTest
)


# CLI parser


def process_args() -> int:
    """Run actions based on CLI arguments."""
    args = build_parser().parse_args()

    if args.debug:
        config.DEBUG = True

    if not hasattr(args, 'func'):
        raise ValueError('Invalid argument(s). Please run "test -h" or "test <subcommand> -h" for help.')

    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI parser."""
    # Help parser
    help_parser = argparse.ArgumentParser(add_help=False)

    group = help_parser.add_argument_group('Help and debug')
    group.add_argument('--debug',
                       help='Enable debug output.',
                       action='store_true')
    group.add_argument('-h', '--help',
                       help='Show this help message and exit.',
                       action='help')

    # Mode parser
    mode_parser = argparse.ArgumentParser(add_help=False)

    group = mode_parser.add_argument_group('Mode')
    group.add_argument('-m', '--mode',
                       choices=TestMode.ALL,
                       default=TestMode.ALL[0],
                       help='Test mode.')

    # Configuration parser
    config_parser = argparse.ArgumentParser(add_help=False)

    group = config_parser.add_argument_group('Configuration')
    group.add_argument('-d', '--datasets',
                       nargs='+',
                       help='Desired datasets.')
    group.add_argument('-r', '--reasoners',
                       nargs='+',
                       help='Desired reasoners.')
    group.add_argument('-n', '--num-iterations',
                       type=positive_int,
                       default=Reasoners.DEFAULT_ITERATIONS,
                       help='Number of iterations for each test.')
    group.add_argument('-f', '--resume-after',
                       help='Resume the test after the specified ontology.')
    group.add_argument('-a', '--all-syntaxes',
                       action='store_true',
                       help='If set, the test is run on all supported syntaxes.')

    # Main parser
    main_parser = argparse.ArgumentParser(prog='test',
                                          description='Test framework for OWL reasoners.',
                                          parents=[help_parser],
                                          add_help=False)

    subparsers = main_parser.add_subparsers(title='Available tests')

    # Classification subcommand
    desc = 'Perform the classification test.'
    parser_classification = subparsers.add_parser('classification',
                                                  description=desc,
                                                  help=desc,
                                                  parents=[help_parser, mode_parser, config_parser],
                                                  add_help=False)

    parser_classification.set_defaults(func=classification_sub)

    # Consistency subcommand
    desc = 'Perform the consistency test.'
    parser_consistency = subparsers.add_parser('consistency',
                                               description=desc,
                                               help=desc,
                                               parents=[help_parser, mode_parser, config_parser],
                                               add_help=False)

    parser_consistency.set_defaults(func=consistency_sub)

    # Abduction/contraction subcommand
    desc = 'Perform the abduction/contraction test.'
    parser_abduction_contraction = subparsers.add_parser('abduction-contraction',
                                                         description=desc,
                                                         help=desc,
                                                         parents=[help_parser, mode_parser, config_parser],
                                                         add_help=False)

    parser_abduction_contraction.set_defaults(func=abduction_contraction_sub)

    # Dataset info subcommand
    desc = 'Print information about the reasoners and datasets.'
    parser_info = subparsers.add_parser('info',
                                        description=desc,
                                        help=desc,
                                        parents=[help_parser, config_parser],
                                        add_help=False)

    parser_info.set_defaults(func=info_sub)

    return main_parser


# Subcommands


def abduction_contraction_sub(args) -> int:
    datasets = args.datasets if args.datasets else ['sisinflab']
    {
        TestMode.CORRECTNESS: NotImplementedTest(),

        TestMode.TIME: AbductionContractionTimeTest(datasets=datasets,
                                                    reasoners=args.reasoners,
                                                    iterations=args.num_iterations),

        TestMode.MEMORY: AbductionContractionMemoryTest(datasets=datasets,
                                                        reasoners=args.reasoners,
                                                        iterations=args.num_iterations),

        TestMode.MOBILE: AbductionContractionMobileTest(datasets=datasets,
                                                        reasoners=args.reasoners,
                                                        iterations=args.num_iterations)
    }[args.mode].start(args.resume_after)
    return 0


def classification_sub(args) -> int:
    {
        TestMode.CORRECTNESS: ClassificationCorrectnessTest(datasets=args.datasets,
                                                            reasoners=args.reasoners),

        TestMode.TIME: ClassificationTimeTest(datasets=args.datasets,
                                              reasoners=args.reasoners,
                                              all_syntaxes=args.all_syntaxes,
                                              iterations=args.num_iterations),

        TestMode.MEMORY: ClassificationMemoryTest(datasets=args.datasets,
                                                  reasoners=args.reasoners,
                                                  all_syntaxes=args.all_syntaxes,
                                                  iterations=args.num_iterations),

        TestMode.MOBILE: ClassificationMobileTest(datasets=args.datasets,
                                                  reasoners=args.reasoners,
                                                  iterations=args.num_iterations)
    }[args.mode].start(args.resume_after)
    return 0


def consistency_sub(args) -> int:
    {
        TestMode.CORRECTNESS: ConsistencyCorrectnessTest(datasets=args.datasets,
                                                         reasoners=args.reasoners),

        TestMode.TIME: ConsistencyTimeTest(datasets=args.datasets,
                                           reasoners=args.reasoners,
                                           all_syntaxes=args.all_syntaxes,
                                           iterations=args.num_iterations),

        TestMode.MEMORY: ConsistencyMemoryTest(datasets=args.datasets,
                                               reasoners=args.reasoners,
                                               all_syntaxes=args.all_syntaxes,
                                               iterations=args.num_iterations),

        TestMode.MOBILE: ConsistencyMobileTest(datasets=args.datasets,
                                               reasoners=args.reasoners,
                                               iterations=args.num_iterations)
    }[args.mode].start(args.resume_after)
    return 0


def info_sub(args) -> int:
    InfoTest(datasets=args.datasets,
             reasoners=args.reasoners).start(args.resume_after)
    return 0


# Utils


def positive_int(value: str) -> int:
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError('{} is not a positive int.'.format(value))
    return ivalue
