import csv
from os import listdir, path
from abc import ABCMeta, abstractmethod, abstractproperty

from src import config
from src.reasoners.owl import OWLOntology, OWLSyntax
from src.utils import echo, exc, fileutils
from src.utils.logger import Logger


class Test(object):
    """Abstract test class."""
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        """:rtype : str"""
        pass

    @abstractmethod
    def run(self, onto_name, ontologies, logger, csv_writer):
        """Runs test over a single ontology.

        :param str onto_name : File name of the ontology.
        :param list[OWLOntology] ontologies : Ontologies in different syntaxes.
        :param Logger logger : Logger instance.
        :param csv.writer csv_writer : CSV writer instance.
        """
        pass

    @abstractmethod
    def setup(self, logger, csv_writer):
        """Called before the test starts iterating on ontologies.

        :param Logger logger : Logger instance.
        :param csv.writer csv_writer : CSV writer instance.
        """
        pass

    def __init__(self, datasets=None):
        """
        :param list[str] datasets : If specified, limit the tests to these datasets.
        """
        self._datasets = datasets

    def start(self):
        """Starts the test."""
        data_dir = config.Paths.DATA_DIR

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
                    func_ontology = OWLOntology(path.join(func_dir, onto_name), OWLSyntax.FUNCTIONAL)
                    xml_ontology = OWLOntology(path.join(xml_dir, onto_name), OWLSyntax.RDFXML)

                    ontologies = [func_ontology, xml_ontology]
                    size_str = ' | '.join(['{}: {}'.format(o.syntax, o.readable_size) for o in ontologies])

                    logger.log('{}'.format(onto_name), color=echo.Color.YELLOW, endl=False)
                    logger.log(' ({})'.format(size_str))

                    self.run(onto_name, ontologies, logger, csv_writer)

                    logger.log('')
