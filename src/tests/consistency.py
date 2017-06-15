from src import config
from src.reasoners.owl import OWLSyntax
from src.utils import echo
from src.utils.proc import WatchdogException
from test import Test


class ConsistencyCorrectnessTest(Test):
    """Consistency correctness test."""

    @property
    def name(self):
        return 'consistency correctness'

    def setup(self, logger, csv_writer):
        del logger  # Unused
        csv_header = ['Ontology']
        csv_header.extend([r.name for r in self._reasoners])
        csv_writer.writerow(csv_header)

    def run(self, onto_name, ontologies, logger, csv_writer):

        csv_row = [onto_name]

        # Check consistency
        for reasoner in self._reasoners:
            logger.log('    {}: '.format(reasoner.name), endl=False)

            try:
                reasoner_results = reasoner.consistency(ontologies[reasoner.preferred_syntax].path,
                                                        timeout=config.Reasoners.CONSISTENCY_TIMEOUT)
            except WatchdogException:
                result = 'timeout'
                color = echo.Color.RED
            except Exception:
                result = 'error'
                color = echo.Color.RED
            else:
                if reasoner_results.consistent:
                    result = 'consistent'
                    color = echo.Color.GREEN
                else:
                    result = 'inconsistent'
                    color = echo.Color.RED

            logger.log(result, color=color)
            csv_row.append(result)

        csv_writer.writerow(csv_row)


class ConsistencyTimeTest(Test):
    """Consistency turnaround time test."""

    @property
    def name(self):
        return 'consistency time'

    def setup(self, logger, csv_writer):
        del logger  # Unused

        columns = ['Ontology']

        for reasoner in self._reasoners:
            for syntax in reasoner.supported_syntaxes if self._all_syntaxes else [reasoner.preferred_syntax]:
                columns.append('{} {} parsing'.format(reasoner.name, syntax))
                columns.append('{} {} consistency'.format(reasoner.name, syntax))

        csv_writer.writerow(columns)

    # noinspection PyBroadException
    def run(self, onto_name, ontologies, logger, csv_writer):

        fail = {syntax: [] for syntax in OWLSyntax.ALL}

        for iteration in xrange(config.Reasoners.CONSISTENCY_ITERATIONS):
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
                        results = reasoner.consistency(ontology.path,
                                                       timeout=config.Reasoners.CONSISTENCY_TIMEOUT)
                    except WatchdogException:
                        csv_row.extend(['timeout', 'timeout'])
                        logger.log('        {}: timeout'.format(syntax))
                        fail[syntax].append(reasoner.name)
                    except Exception:
                        csv_row.extend(['error', 'error'])
                        logger.log('        {}: error'.format(syntax))
                        fail[syntax].append(reasoner.name)
                    else:
                        stats = results.stats
                        csv_row.extend([stats.parsing_ms, stats.reasoning_ms])
                        logger.log('        ', endl=False)
                        logger.log('{}: Parsing {:.0f} ms | Consistency {:.0f} ms'.format(syntax,
                                                                                          stats.parsing_ms,
                                                                                          stats.reasoning_ms))
            logger.log('')
            csv_writer.writerow(csv_row)
