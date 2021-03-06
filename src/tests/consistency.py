from subprocess import TimeoutExpired

from src.config import Reasoners
from src.reasoners.owl import ReasoningTask, TestMode
from src.pyutils import echo, fileutils
from .test import Test, StandardPerformanceTest


class ConsistencyCorrectnessTest(Test):
    """Consistency correctness test."""

    @property
    def name(self):
        return 'consistency correctness'

    @property
    def default_reasoners(self):
        return Reasoners.desktop(Reasoners.supporting_task(ReasoningTask.CONSISTENCY))

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
                                                        timeout=Reasoners.CONSISTENCY_TIMEOUT)
            except TimeoutExpired:
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
    def default_reasoners(self):
        return Reasoners.desktop(Reasoners.supporting_task(ReasoningTask.CONSISTENCY))

    @property
    def result_fields(self):
        return ['parsing', 'consistency']

    def run_reasoner(self, reasoner, ontology, logger):

        results = reasoner.consistency(ontology.path,
                                       timeout=Reasoners.CONSISTENCY_TIMEOUT,
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
    def default_reasoners(self):
        return Reasoners.desktop(Reasoners.supporting_task(ReasoningTask.CONSISTENCY))

    @property
    def result_fields(self):
        return ['memory']

    def run_reasoner(self, reasoner, ontology, logger):
        results = reasoner.consistency(ontology.path,
                                       timeout=Reasoners.CONSISTENCY_TIMEOUT,
                                       mode=TestMode.MEMORY)
        stats = results.stats

        logger.log('{}: {}'.format(ontology.syntax, fileutils.human_readable_bytes(stats.max_memory)))

        return [stats.max_memory]


class ConsistencyMobileTest(StandardPerformanceTest):
    """Mobile consistency performance test."""

    @property
    def name(self):
        return 'consistency mobile'

    @property
    def default_reasoners(self):
        return Reasoners.mobile(Reasoners.supporting_task(ReasoningTask.CONSISTENCY))

    @property
    def result_fields(self):
        return ['parsing', 'consistency', 'memory']

    def run_reasoner(self, reasoner, ontology, logger):

        stats = reasoner.consistency(ontology.path, timeout=Reasoners.CONSISTENCY_TIMEOUT).stats
        human_readable_memory = fileutils.human_readable_bytes(stats.max_memory)

        logger.log('Parsing {:.0f} ms | Consistency {:.0f} ms | Memory {}'.format(stats.parsing_ms,
                                                                                  stats.reasoning_ms,
                                                                                  human_readable_memory))
        return [stats.parsing_ms, stats.reasoning_ms, stats.max_memory]
