import filecmp
import os

from src import config
from src.utils import echo, fileutils
from test import Test


class ClassificationCorrectnessTest(Test):
    """Classification correctness test."""

    @property
    def name(self):
        return 'classification correctness'

    def __init__(self):
        self.reference_out = os.path.join(config.Paths.TEMP_DIR, 'reference.txt')
        self.minime_out = os.path.join(config.Paths.TEMP_DIR, 'minime.txt')

    def setup(self, logger, csv_writer):
        csv_writer.writerow(['Ontology', 'Result', 'Failure reason'])

    def run(self, func_ontology, xml_ontology, logger, csv_writer):

        fileutils.remove_dir_contents(config.Paths.TEMP_DIR)

        reference = config.Reasoners.reference
        minime = config.Reasoners.miniME

        # Classify
        logger.log('{}: '.format(minime.name), endl=False)
        stats = minime.classify(xml_ontology.path, output_file=self.minime_out)
        logger.log('{:.0f} ms'.format(stats.reasoning_ms), endl=False)

        logger.log(' | {}: '.format(reference.name), endl=False)
        stats = reference.classify(func_ontology.path, output_file=self.reference_out)
        logger.log('{:.0f} ms'.format(stats.reasoning_ms))

        # Results
        logger.log('Result: ', endl=False)

        if filecmp.cmp(self.reference_out, self.minime_out, shallow=False):
            logger.log('success', color=echo.Color.GREEN)
            csv_writer.writerow([func_ontology.name, 'success'])
        else:
            logger.log('failure', color=echo.Color.RED)

            # Attempt to detect failure reason
            logger.log('Reason: ', endl=False)

            if 'raptor error -' in stats.error:
                reason = 'raptor parsing error'
            elif fileutils.contains(xml_ontology, '// General axioms'):
                reason = 'contains general concept inclusions'
            else:
                reason = 'unknown'

            logger.log(reason, color=echo.Color.YELLOW)
            csv_writer.writerow([func_ontology.name, 'failure', reason])


class ClassificationTimeTest(Test):
    """Classification turnaround time test."""

    @property
    def name(self):
        return 'classification time'

    def setup(self, logger, csv_writer):
        reasoners = [r.name for r in config.Reasoners.third_party]
        csv_writer.writerow(['Ontology', config.Reasoners.miniME.name] + reasoners)

    def run(self, func_ontology, xml_ontology, logger, csv_writer):

        minime = config.Reasoners.miniME
        results = []

        logger.log('{}: '.format(minime.name), endl=False)
        stats = minime.classify(xml_ontology.path)
        results.append(stats.reasoning_ms)
        logger.log('{:.0f} ms'.format(stats.reasoning_ms))

        for reasoner in config.Reasoners.third_party:
            logger.log('{}: '.format(reasoner.name), endl=False)
            stats = reasoner.classify(func_ontology.path)
            results.append(stats.reasoning_ms)
            logger.log('{:.0f} ms'.format(stats.reasoning_ms))

        csv_writer.writerow([xml_ontology.name] + results)
