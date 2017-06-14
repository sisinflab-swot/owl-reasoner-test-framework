import filecmp
import os

from src import config
from src.reasoners.owl import OWLSyntax
from src.utils import echo, fileutils
from src.utils.proc import WatchdogException
from test import Test


class ClassificationCorrectnessTest(Test):
    """Classification correctness test."""

    @property
    def name(self):
        return 'classification correctness'

    def setup(self, logger, csv_writer):
        del logger  # Unused
        csv_writer.writerow(['Ontology', 'Result', 'Failure reason'])

    def run(self, onto_name, ontologies, logger, csv_writer):

        fileutils.remove_dir_contents(config.Paths.TEMP_DIR)

        reference = config.Reasoners.reference
        minime = config.Reasoners.miniME

        reference_out = os.path.join(config.Paths.TEMP_DIR, 'reference.txt')
        minime_out = os.path.join(config.Paths.TEMP_DIR, 'minime.txt')

        xml_ontology = ontologies[OWLSyntax.RDFXML]
        func_ontology = ontologies[OWLSyntax.FUNCTIONAL]

        # Classify
        logger.log('{}: '.format(minime.name), endl=False)
        minime_stats = minime.classify(xml_ontology.path, output_file=minime_out)
        logger.log('Parsing {:.0f} ms | Classification {:.0f} ms'.format(minime_stats.parsing_ms,
                                                                         minime_stats.reasoning_ms))

        logger.log('{}: '.format(reference.name), endl=False)
        ref_stats = reference.classify(func_ontology.path, output_file=reference_out)
        logger.log('Parsing {:.0f} ms | Classification {:.0f} ms'.format(ref_stats.parsing_ms,
                                                                         ref_stats.reasoning_ms))

        # Results
        logger.log('Result: ', endl=False)

        if filecmp.cmp(reference_out, minime_out, shallow=False):
            logger.log('success', color=echo.Color.GREEN)
            csv_writer.writerow([onto_name, 'success'])
        else:
            logger.log('failure', color=echo.Color.RED)

            # Attempt to detect failure reason
            logger.log('Reason: ', endl=False)

            if 'raptor error -' in minime_stats.error:
                reason = 'raptor parsing error'
            elif fileutils.contains(xml_ontology.path, '// General axioms'):
                reason = 'contains general concept inclusions'
            else:
                reason = 'unknown'

            logger.log(reason, color=echo.Color.YELLOW)
            csv_writer.writerow([onto_name, 'failure', reason])


class ClassificationTimeTest(Test):
    """Classification turnaround time test."""

    @property
    def name(self):
        return 'classification time'

    def setup(self, logger, csv_writer):
        del logger  # Unused

        columns = ['Ontology']

        for reasoner in self._reasoners:
            for syntax in reasoner.supported_syntaxes:
                columns.append('{} {} parsing'.format(reasoner.name, syntax))
                columns.append('{} {} classification'.format(reasoner.name, syntax))

        csv_writer.writerow(columns)

    # noinspection PyBroadException
    def run(self, onto_name, ontologies, logger, csv_writer):

        csv_row = [onto_name]

        for reasoner in self._reasoners:
            logger.log('- {}:'.format(reasoner.name))
            syntaxes = reasoner.supported_syntaxes if self._all_syntaxes else [reasoner.preferred_syntax]

            for syntax in syntaxes:
                ontology = ontologies[syntax]

                try:
                    stats = reasoner.classify(ontology.path, timeout=config.Reasoners.classification_timeout)
                except WatchdogException:
                    csv_row.extend(['timeout', 'timeout'])
                    logger.log('    {}: timeout'.format(syntax))
                except Exception:
                    csv_row.extend(['error', 'error'])
                    logger.log('    {}: error'.format(syntax))
                else:
                    csv_row.extend([stats.parsing_ms, stats.reasoning_ms])
                    logger.log('    {}: Parsing {:.0f} ms | Classification {:.0f} ms'.format(syntax,
                                                                                             stats.parsing_ms,
                                                                                             stats.reasoning_ms))

        csv_writer.writerow(csv_row)
