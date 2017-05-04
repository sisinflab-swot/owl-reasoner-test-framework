import filecmp
import os

from src import config
from src.utils import echo, fileutils
from src.utils.logger import Logger


def correctness():
    """Performs the classification correctness test."""
    __test(check_correctness=True)


def turnaround_time():
    """Performs the classification turnaround time test."""
    __test(check_correctness=False)


def __test(check_correctness):
    """Private test function.

    :param bool check_correctness : True if correctness should be checked, false otherwise.
    """

    # Variables
    if check_correctness:
        reference_out = os.path.join(config.Paths.TEMP_DIR, 'reference.txt')
        minime_out = os.path.join(config.Paths.TEMP_DIR, 'minime.txt')
    else:
        reference_out = None
        minime_out = None

    ontologies = [f for f in os.listdir(config.Paths.FUNC_DIR) if f.endswith('.owl')]
    logger = Logger(config.Paths.LOG)

    konclude = config.Reasoners.konclude
    minime = config.Reasoners.miniME

    # Hello
    echo.pretty('Starting classification on {} ontologies, this may take a while...'.format(len(ontologies)),
                color=echo.Color.GREEN)

    # Cleanup
    fileutils.create_dir(config.Paths.WRK_DIR)
    fileutils.create_dir(config.Paths.TEMP_DIR)
    fileutils.remove_dir_contents(config.Paths.TEMP_DIR)
    logger.clear()

    # Start test
    for onto_name in ontologies:
        func_ontology = os.path.join(config.Paths.FUNC_DIR, onto_name)
        func_ontology_size = fileutils.human_readable_size(func_ontology)

        xml_ontology = os.path.join(config.Paths.XML_DIR, onto_name)
        xml_ontology_size = fileutils.human_readable_size(xml_ontology)

        logger.log(onto_name, color=echo.Color.YELLOW, endl=False)
        logger.log(' (Functional: {} | RDFXML: {})'.format(func_ontology_size, xml_ontology_size))

        fileutils.remove_dir_contents(config.Paths.TEMP_DIR)

        # Classify
        logger.log('{}: '.format(konclude.name), endl=False)
        stats = konclude.classify(func_ontology, output_file=reference_out)
        logger.log('{:.0f} ms'.format(stats.reasoning_ms), endl=False)

        logger.log(' | {}: '.format(minime.name), endl=False)
        stats = minime.classify(xml_ontology, output_file=minime_out)
        logger.log('{:.0f} ms'.format(stats.reasoning_ms))

        if check_correctness:
            # Results
            logger.log('Result: ', endl=False)

            if filecmp.cmp(reference_out, minime_out, shallow=False):
                success = True
                logger.log('success', color=echo.Color.GREEN)
            else:
                success = False
                logger.log('failure', color=echo.Color.RED)

            if not success:
                # Attempt to detect failure reason
                logger.log('Reason: ', endl=False)

                if 'raptor error -' in stats.error:
                    reason = 'raptor parsing error'
                elif fileutils.contains(xml_ontology, '// General axioms'):
                    reason = 'contains general concept inclusions'
                else:
                    reason = 'unknown'

                logger.log(reason, color=echo.Color.YELLOW)

        logger.log('')
