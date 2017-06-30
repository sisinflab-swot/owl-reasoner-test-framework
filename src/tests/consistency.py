from src import config
from src.reasoners.owl import TestMode
from src.utils import echo, fileutils
from src.utils.proc import WatchdogException
from test import Test, StandardPerformanceTest


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
            logger.log('{}: '.format(reasoner.name), endl=False)

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


class ConsistencyTimeTest(StandardPerformanceTest):
    """Consistency turnaround time test."""

    @property
    def name(self):
        return 'consistency time'

    @property
    def result_fields(self):
        return ['parsing', 'consistency']

    def run_reasoner(self, reasoner, ontology, logger):

        results = reasoner.consistency(ontology.path,
                                       timeout=config.Reasoners.CONSISTENCY_TIMEOUT,
                                       mode=TestMode.TIME)

        stats = results.stats
        logger.log('{}: Parsing {:.0f} ms | Consistency {:.0f} ms'.format(ontology.syntax,
                                                                          stats.parsing_ms,
                                                                          stats.reasoning_ms))
        return [stats.parsing_ms, stats.reasoning_ms]


class ConsistencyMemoryTest(StandardPerformanceTest):
    """Consistency memory test."""

    @property
    def name(self):
        return 'consistency memory'

    @property
    def result_fields(self):
        return ['memory']

    def run_reasoner(self, reasoner, ontology, logger):
        results = reasoner.consistency(ontology.path,
                                       timeout=config.Reasoners.CONSISTENCY_TIMEOUT,
                                       mode=TestMode.MEMORY)
        stats = results.stats

        logger.log('{}: {}'.format(ontology.syntax, fileutils.human_readable_bytes(stats.max_memory)))

        return [stats.max_memory]
