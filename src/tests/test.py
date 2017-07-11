import csv
from os import listdir, path
from abc import ABCMeta, abstractmethod, abstractproperty

from src import config
from src.reasoners.owl import OWLOntology, OWLSyntax
from src.utils import echo, exc, fileutils
from src.utils.logger import Logger
from src.utils.proc import WatchdogException


class Test(object):
    """Abstract test class."""
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        """:rtype : str"""
        pass

    @abstractmethod
    def setup(self, logger, csv_writer):
        """Called before the test starts iterating on ontologies.

        :param Logger logger : Logger instance.
        :param csv.writer csv_writer : CSV writer instance.
        """
        pass

    @abstractmethod
    def run(self, onto_name, ontologies, logger, csv_writer):
        """Runs test over a single ontology.

        :param str onto_name : File name of the ontology.
        :param dict[str, OWLOntology] ontologies : Ontologies by syntax.
        :param Logger logger : Logger instance.
        :param csv.writer csv_writer : CSV writer instance.
        """
        pass

    def __init__(self, datasets=None, reasoners=None, all_syntaxes=False):
        """
        :param list[str] datasets : If specified, limit the tests to the specified datasets.
        :param list[str] reasoners : If specified, limit the tests to the specified reasoners.
        :param bool all_syntaxes : If true, the test is run on all supported syntaxes.
        """
        self._datasets = datasets
        self._all_syntaxes = all_syntaxes

        if reasoners:
            self._reasoners = [config.Reasoners.BY_NAME[n] for n in reasoners]
        else:
            self._reasoners = config.Reasoners.ALL_DESKTOP

    def start(self, resume_ontology=None):
        """Starts the test.

        :param str resume_ontology : The ontology from which the test should be resumed.
        """
        data_dir = config.Paths.DATA_DIR
        search_for_resume = True if resume_ontology else False

        if self._datasets:
            datasets = [path.join(data_dir, d) for d in self._datasets]
        else:
            datasets = [path.join(data_dir, d) for d in listdir(data_dir)]
            datasets = [d for d in datasets if path.isdir(d)]

        with Logger(config.Paths.LOG) as logger, open(config.Paths.RESULTS, mode='wb') as csv_file:

            fileutils.create_dir(config.Paths.WRK_DIR)
            fileutils.create_dir(config.Paths.TEMP_DIR)
            fileutils.remove_dir_contents(config.Paths.TEMP_DIR)

            logger.clear()
            csv_writer = csv.writer(csv_file)

            self.setup(logger, csv_writer)

            for dataset in datasets:
                func_dir = path.join(dataset, 'functional')
                xml_dir = path.join(dataset, 'rdfxml')

                exc.raise_if_not_found(func_dir, file_type='dir')
                exc.raise_if_not_found(xml_dir, file_type='dir')

                onto_names = [f for f in listdir(func_dir) if f.endswith('.owl')]

                # Hello
                echo.pretty(
                    'Starting {} test on "{}" dataset ({} ontologies)...'.format(self.name,
                                                                                 path.basename(dataset),
                                                                                 len(onto_names)),
                    color=echo.Color.GREEN)

                # Test dataset
                for onto_name in onto_names:

                    # Allow resuming the test after a certain ontology.
                    if search_for_resume:
                        if onto_name == resume_ontology:
                            search_for_resume = False
                        continue

                    func_ontology = OWLOntology(path.join(func_dir, onto_name), OWLSyntax.FUNCTIONAL)
                    xml_ontology = OWLOntology(path.join(xml_dir, onto_name), OWLSyntax.RDFXML)

                    ontologies = {
                        OWLSyntax.FUNCTIONAL: func_ontology,
                        OWLSyntax.RDFXML: xml_ontology
                    }

                    size_str = ' | '.join(['{}: {}'.format(o.syntax, o.readable_size) for o in ontologies.values()])

                    logger.log('{}'.format(onto_name), color=echo.Color.YELLOW, endl=False)
                    logger.log(' ({})'.format(size_str))
                    logger.indent_level += 1

                    try:
                        self.run(onto_name, ontologies, logger, csv_writer)
                    except Exception as e:
                        if config.debug:
                            raise e
                        else:
                            err_msg = e.message if e.message else str(e)
                            echo.error(err_msg)
                    finally:
                        logger.indent_level -= 1

                    logger.log('')


# noinspection PyTypeChecker
class StandardPerformanceTest(Test):
    """Abstract test class for measuring the performance of standard reasoning tasks."""
    __metaclass__ = ABCMeta

    @abstractproperty
    def result_fields(self):
        """:rtype : list[str]"""
        pass

    @abstractmethod
    def run_reasoner(self, reasoner, ontology, logger):
        """Called every run, for each reasoner and each ontology.

        :param Reasoner reasoner : The reasoner.
        :param Ontology ontology : The ontology.
        :param Logger logger : Logger instance.
        :rtype : list[str]
        :return : Values for the CSV result fields.
        """
        pass

    def __init__(self, datasets=None, reasoners=None, all_syntaxes=False, iterations=1):
        """
        :param list[str] datasets : If specified, limit the tests to the specified datasets.
        :param list[str] reasoners : If specified, limit the tests to the specified reasoners.
        :param bool all_syntaxes : If true, the test is run on all supported syntaxes.
        :param int iterations : Number of iterations per ontology.
        """
        Test.__init__(self, datasets, reasoners, all_syntaxes)
        self.iterations = iterations

    def setup(self, logger, csv_writer):
        del logger  # Unused
        csv_header = ['Ontology']

        for reasoner in self._reasoners:
            for syntax in reasoner.supported_syntaxes if self._all_syntaxes else [reasoner.preferred_syntax]:
                for field in self.result_fields:
                    csv_header.append('{} {} {}'.format(reasoner.name, syntax, field))

        csv_writer.writerow(csv_header)

    def run(self, onto_name, ontologies, logger, csv_writer):

        fail = {syntax: [] for syntax in OWLSyntax.ALL}

        for iteration in xrange(self.iterations):
            logger.log('Run {}:'.format(iteration + 1), color=echo.Color.YELLOW)
            logger.indent_level += 1

            csv_row = [onto_name]

            for reasoner in self._reasoners:
                logger.log('- {}:'.format(reasoner.name))
                logger.indent_level += 1

                syntaxes = reasoner.supported_syntaxes if self._all_syntaxes else [reasoner.preferred_syntax]

                for syntax in syntaxes:
                    # Skip already failed or timed out.
                    if reasoner.name in fail[syntax]:
                        csv_row.extend(['skip'] * len(self.result_fields))
                        logger.log('{}: skip'.format(syntax))
                        continue

                    ontology = ontologies[syntax]

                    try:
                        csv_row.extend(self.run_reasoner(reasoner, ontology, logger))
                    except WatchdogException:
                        csv_row.extend(['timeout'] * len(self.result_fields))
                        logger.log('{}: timeout'.format(syntax))
                        fail[syntax].append(reasoner.name)
                    except Exception as e:
                        if config.debug:
                            raise e

                        csv_row.extend(['error'] * len(self.result_fields))
                        logger.log('{}: error'.format(syntax))
                        fail[syntax].append(reasoner.name)

                logger.indent_level -= 1

            logger.indent_level -= 1
            logger.log('')
            csv_writer.writerow(csv_row)


class NotImplementedTest(Test):
    """Not implemented test."""

    @property
    def name(self):
        return 'not implemented'

    def setup(self, logger, csv_writer):
        del logger, csv_writer  # Unused
        raise NotImplementedError('Not implemented.')

    def run(self, onto_name, ontologies, logger, csv_writer):
        del onto_name, ontologies, logger, csv_writer  # Unused
        pass
