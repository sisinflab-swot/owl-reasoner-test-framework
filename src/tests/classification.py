import filecmp
import os
from subprocess import TimeoutExpired

from src.config import Reasoners
from src.reasoners.owl import ReasoningTask, TestMode
from src.pyutils import echo, fileutils
from .test import Test, StandardPerformanceTest


class ClassificationCorrectnessTest(Test):
    """Classification correctness test."""

    @property
    def name(self):
        return 'classification correctness'

    @property
    def default_reasoners(self):
        return Reasoners.desktop(Reasoners.supporting_task(ReasoningTask.CLASSIFICATION))

    def setup(self, logger, csv_writer):
        del logger  # Unused

        csv_header = ['Ontology']

        for reasoner in [r for r in self._reasoners if r.name != Reasoners.REFERENCE.name]:
            csv_header.append(reasoner.name)

        csv_writer.writerow(csv_header)

    def run(self, onto_name, ontologies, logger, csv_writer):
        self.clear_temp()

        reference = Reasoners.REFERENCE
        reasoner_out = os.path.join(self.temp_dir, 'reasoner.txt')
        reference_out = os.path.join(self.temp_dir, 'reference.txt')

        csv_row = [onto_name]

        # Classify
        logger.log('{}: '.format(reference.name), endl=False)
        logger.indent_level += 1

        reference.classify(ontologies[reference.preferred_syntax].path,
                           output_file=reference_out,
                           timeout=Reasoners.CLASSIFICATION_TIMEOUT)
        logger.log('done', color=echo.Color.GREEN)

        for reasoner in [r for r in self._reasoners if r.name != reference.name]:
            logger.log('{}: '.format(reasoner.name), endl=False)

            try:
                reasoner.classify(ontologies[reasoner.preferred_syntax].path,
                                  output_file=reasoner_out,
                                  timeout=Reasoners.CLASSIFICATION_TIMEOUT)
            except TimeoutExpired:
                result = 'timeout'
                color = echo.Color.RED
            except Exception:
                result = 'error'
                color = echo.Color.RED
            else:
                if filecmp.cmp(reasoner_out, reference_out, shallow=False):
                    result = 'same'
                    color = echo.Color.GREEN
                else:
                    result = 'different'
                    color = echo.Color.RED

            logger.log(result, color=color)
            csv_row.append(result)

        logger.indent_level -= 1
        csv_writer.writerow(csv_row)


class ClassificationTimeTest(StandardPerformanceTest):
    """Classification turnaround time test."""

    @property
    def name(self):
        return 'classification time'

    @property
    def default_reasoners(self):
        return Reasoners.desktop(Reasoners.supporting_task(ReasoningTask.CLASSIFICATION))

    @property
    def result_fields(self):
        return ['parsing', 'classification']

    def run_reasoner(self, reasoner, ontology, logger):

        stats = reasoner.classify(ontology.path,
                                  timeout=Reasoners.CLASSIFICATION_TIMEOUT,
                                  mode=TestMode.TIME)

        logger.log('{}: Parsing {:.0f} ms | Classification {:.0f} ms'.format(ontology.syntax,
                                                                             stats.parsing_ms,
                                                                             stats.reasoning_ms))
        return [stats.parsing_ms, stats.reasoning_ms]


class ClassificationMemoryTest(StandardPerformanceTest):
    """Classification memory test."""

    @property
    def name(self):
        return 'classification memory'

    @property
    def default_reasoners(self):
        return Reasoners.desktop(Reasoners.supporting_task(ReasoningTask.CLASSIFICATION))

    @property
    def result_fields(self):
        return ['memory']

    def run_reasoner(self, reasoner, ontology, logger):

        stats = reasoner.classify(ontology.path,
                                  timeout=Reasoners.CLASSIFICATION_TIMEOUT,
                                  mode=TestMode.MEMORY)

        logger.log('{}: {}'.format(ontology.syntax, fileutils.human_readable_bytes(stats.max_memory)))

        return [stats.max_memory]


class ClassificationMobileTest(StandardPerformanceTest):
    """Mobile classification performance test."""

    @property
    def name(self):
        return 'classification mobile'

    @property
    def default_reasoners(self):
        return Reasoners.mobile(Reasoners.supporting_task(ReasoningTask.CLASSIFICATION))

    @property
    def result_fields(self):
        return ['parsing', 'classification', 'memory']

    def run_reasoner(self, reasoner, ontology, logger):

        stats = reasoner.classify(ontology.path, timeout=Reasoners.CLASSIFICATION_TIMEOUT)
        human_readable_memory = fileutils.human_readable_bytes(stats.max_memory)

        logger.log('Parsing {:.0f} ms | Classification {:.0f} ms | Memory {}'.format(stats.parsing_ms,
                                                                                     stats.reasoning_ms,
                                                                                     human_readable_memory))
        return [stats.parsing_ms, stats.reasoning_ms, stats.max_memory]
