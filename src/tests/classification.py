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

        csv_header = ['Ontology']

        for reasoner in [r for r in self._reasoners if r.name != config.Reasoners.MINIME.name]:
            csv_header.append(reasoner.name)

        csv_writer.writerow(csv_header)

    def run(self, onto_name, ontologies, logger, csv_writer):

        fileutils.remove_dir_contents(config.Paths.TEMP_DIR)

        minime = config.Reasoners.MINIME
        reference_out = os.path.join(config.Paths.TEMP_DIR, 'reference.txt')
        minime_out = os.path.join(config.Paths.TEMP_DIR, 'minime.txt')

        csv_row = [onto_name]

        # Classify
        logger.log('    {}: '.format(minime.name), endl=False)
        minime.classify(ontologies[minime.preferred_syntax].path,
                        output_file=minime_out,
                        timeout=config.Reasoners.CLASSIFICATION_TIMEOUT)
        logger.log('done', color=echo.Color.GREEN)

        for reasoner in [r for r in self._reasoners if r.name != minime.name]:
            logger.log('        {}: '.format(reasoner.name), endl=False)

            try:
                reasoner.classify(ontologies[reasoner.preferred_syntax].path,
                                  output_file=reference_out,
                                  timeout=config.Reasoners.CLASSIFICATION_TIMEOUT)
            except WatchdogException:
                result = 'timeout'
                color = echo.Color.RED
            except Exception:
                result = 'error'
                color = echo.Color.RED
            else:
                if filecmp.cmp(reference_out, minime_out, shallow=False):
                    result = 'same'
                    color = echo.Color.GREEN
                else:
                    result = 'different'
                    color = echo.Color.RED

            logger.log(result, color=color)
            csv_row.append(result)

        csv_writer.writerow(csv_row)


class ClassificationTimeTest(Test):
    """Classification turnaround time test."""

    @property
    def name(self):
        return 'classification time'

    def setup(self, logger, csv_writer):
        del logger  # Unused

        columns = ['Ontology']

        for reasoner in self._reasoners:
            for syntax in reasoner.supported_syntaxes if self._all_syntaxes else [reasoner.preferred_syntax]:
                columns.append('{} {} parsing'.format(reasoner.name, syntax))
                columns.append('{} {} classification'.format(reasoner.name, syntax))

        csv_writer.writerow(columns)

    # noinspection PyBroadException
    def run(self, onto_name, ontologies, logger, csv_writer):

        fail = {syntax: [] for syntax in OWLSyntax.ALL}

        for iteration in xrange(config.Reasoners.CLASSIFICATION_ITERATIONS):
            logger.log('Run {}:'.format(iteration + 1))

            csv_row = [onto_name]

            for reasoner in self._reasoners:
                logger.log('    - {}:'.format(reasoner.name))
                syntaxes = reasoner.supported_syntaxes if self._all_syntaxes else [reasoner.preferred_syntax]

                for syntax in syntaxes:
                    # Skip already failed or timed out.
                    if reasoner.name in fail[syntax]:
                        csv_row.extend(['skip', 'skip'])
                        logger.log('        {}: skip'.format(syntax))
                        continue

                    ontology = ontologies[syntax]

                    try:
                        stats = reasoner.classify(ontology.path,
                                                  timeout=config.Reasoners.CLASSIFICATION_TIMEOUT)
                    except WatchdogException:
                        csv_row.extend(['timeout', 'timeout'])
                        logger.log('        {}: timeout'.format(syntax))
                        fail[syntax].append(reasoner.name)
                    except Exception:
                        csv_row.extend(['error', 'error'])
                        logger.log('        {}: error'.format(syntax))
                        fail[syntax].append(reasoner.name)
                    else:
                        csv_row.extend([stats.parsing_ms, stats.reasoning_ms])
                        logger.log('        ', endl=False)
                        logger.log('{}: Parsing {:.0f} ms | Classification {:.0f} ms'.format(syntax,
                                                                                             stats.parsing_ms,
                                                                                             stats.reasoning_ms))
            logger.log('')
            csv_writer.writerow(csv_row)
