import os
from abc import ABCMeta, abstractmethod, abstractproperty

from src import config
from src.reasoners.owl import OWLSyntax, TestMode
from src.utils import echo, fileutils
from src.utils.proc import WatchdogException
from test import Test


# noinspection PyTypeChecker
class AbductionContractionPerformanceTest(Test):
    """Abduction/contraction performance test."""
    __metaclass__ = ABCMeta

    @abstractproperty
    def result_fields(self):
        """:rtype : list[str]"""
        pass

    @abstractmethod
    def run_reasoner(self, reasoner, resource, request, logger):
        """Called every run, for each reasoner and each ontology.

        :param Reasoner reasoner : The reasoner.
        :param Ontology resource : The resource ontology.
        :param Ontology request : The request ontology.
        :param Logger logger : Logger instance.
        :rtype : list[str]
        :return : Values for the CSV result fields.
        """
        pass

    def __init__(self, datasets=None, reasoners=None, iterations=1):
        """
        :param list[str] datasets : If specified, limit the tests to the specified datasets.
        :param list[str] reasoners : If specified, limit the tests to the specified reasoners.
        :param int iterations : Number of iterations per ontology.
        """
        Test.__init__(self, datasets, reasoners)
        self._iterations = iterations

    def setup(self, logger, csv_writer):
        del logger  # Unused
        csv_header = ['Resource', 'Request']

        for reasoner in self._reasoners:
            for field in self.result_fields:
                csv_header.append('{} {}'.format(reasoner.name, field))

        csv_writer.writerow(csv_header)

    def run(self, onto_name, ontologies, logger, csv_writer):

        resource = ontologies[OWLSyntax.RDFXML].path

        dataset_dir = os.path.dirname(os.path.dirname(resource))
        requests_dir = os.path.join(dataset_dir, 'requests', os.path.splitext(onto_name)[0])

        requests = [os.path.join(requests_dir, f) for f in os.listdir(requests_dir) if f.endswith('.owl')]

        if len(requests) == 0:
            logger.log('No available requests.')
            return

        for iteration in xrange(self._iterations):
            logger.log('Run {}:'.format(iteration + 1), color=echo.Color.YELLOW)
            logger.indent_level += 1

            for request in requests:
                request_name = os.path.basename(request)
                logger.log('Request: {}'.format(request_name))
                logger.indent_level += 1

                csv_row = [onto_name, request_name]

                for reasoner in self._reasoners:
                    logger.log('- {}: '.format(reasoner.name), endl=False)
                    try:
                        csv_row.extend(self.run_reasoner(reasoner, resource, request, logger))
                    except WatchdogException:
                        csv_row.extend(['timeout', 'timeout', 'timeout', 'timeout'])
                        logger.log('timeout')
                    except Exception:
                        csv_row.extend(['error', 'error', 'error', 'error'])
                        logger.log('error')

                logger.indent_level -= 1
                csv_writer.writerow(csv_row)

            logger.indent_level -= 1
            logger.log('')


class AbductionContractionTimeTest(AbductionContractionPerformanceTest):
    """Abduction/contraction time test."""

    @property
    def name(self):
        return 'abduction/contraction time'

    @property
    def result_fields(self):
        return ['resource parsing', 'request parsing', 'reasoner init', 'reasoning']

    def run_reasoner(self, reasoner, resource, request, logger):

        stats = reasoner.abduction_contraction(resource, request,
                                               timeout=config.Reasoners.ABDUCTION_CONTRACTION_TIMEOUT,
                                               mode=TestMode.TIME)

        logger.log(('Resource parsing {:.0f} ms | '
                    'Request parsing {:.0f} ms | '
                    'Reasoner init {:.0f} ms | '
                    'Reasoning {:.0f} ms').format(stats.resource_parsing_ms,
                                                  stats.request_parsing_ms,
                                                  stats.init_ms,
                                                  stats.reasoning_ms))

        return [stats.resource_parsing_ms, stats.request_parsing_ms, stats.init_ms, stats.reasoning_ms]


class AbductionContractionMemoryTest(AbductionContractionPerformanceTest):
    """Abduction/contraction memory test."""

    @property
    def name(self):
        return 'abduction/contraction memory'

    @property
    def result_fields(self):
        return ['memory']

    def run_reasoner(self, reasoner, resource, request, logger):

        stats = reasoner.abduction_contraction(resource, request,
                                               timeout=config.Reasoners.ABDUCTION_CONTRACTION_TIMEOUT,
                                               mode=TestMode.MEMORY)

        logger.log('Max memory: {}'.format(fileutils.human_readable_bytes(stats.max_memory)))

        return [stats.max_memory]
