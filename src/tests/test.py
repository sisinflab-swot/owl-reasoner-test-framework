import csv
import os
from abc import ABCMeta, abstractmethod, abstractproperty

from src import config
from src.reasoners.owl import OWLOntology, OWLSyntax
from src.utils import echo, fileutils
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

    def start(self):
        """Starts the test."""
        onto_names = [f for f in os.listdir(config.Paths.FUNC_DIR) if f.endswith('.owl')]
        logger = Logger(config.Paths.LOG)

        # Hello
        echo.pretty('Starting {} test on {} ontologies, this may take a while...'.format(self.name, len(onto_names)),
                    color=echo.Color.GREEN)

        # Setup/cleanup
        fileutils.create_dir(config.Paths.WRK_DIR)
        fileutils.create_dir(config.Paths.TEMP_DIR)
        fileutils.remove_dir_contents(config.Paths.TEMP_DIR)
        logger.clear()

        # Start test
        with logger, open(config.Paths.RESULTS, mode='wb') as csv_file:
            csv_writer = csv.writer(csv_file)
            self.setup(logger, csv_writer)

            for onto_name in onto_names:
                func_ontology = OWLOntology(os.path.join(config.Paths.FUNC_DIR, onto_name), OWLSyntax.FUNCTIONAL)
                xml_ontology = OWLOntology(os.path.join(config.Paths.XML_DIR, onto_name), OWLSyntax.RDFXML)

                ontologies = [func_ontology, xml_ontology]
                size_str = ' | '.join(['{}: {}'.format(o.syntax, o.readable_size) for o in ontologies])

                logger.log('{}'.format(onto_name), color=echo.Color.YELLOW, endl=False)
                logger.log(' ({})'.format(size_str))

                self.run(onto_name, ontologies, logger, csv_writer)

                logger.log('')
