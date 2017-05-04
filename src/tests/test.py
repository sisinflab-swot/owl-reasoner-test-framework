import os
from abc import ABCMeta, abstractmethod, abstractproperty

from src import config
from src.utils import echo, exc, fileutils
from src.utils.logger import Logger


class Ontology(object):
    """Models ontology files."""

    @property
    def name(self):
        """:rtype : str"""
        return os.path.basename(self.path)

    @property
    def readable_size(self):
        """:rtype : str"""
        return fileutils.human_readable_size(self.path)

    def __init__(self, path):
        """:param str path : The path of the ontology."""
        exc.raise_if_not_found(path, file_type='file')
        self.path = path


class Test(object):
    """Abstract test class."""
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        """:rtype : str"""
        pass

    @abstractmethod
    def run(self, func_ontology, xml_ontology, logger):
        """Runs test over a single ontology.

        :param Ontology func_ontology : Functional syntax ontology.
        :param Ontology xml_ontology : RDF/XML syntax ontology.
        :param Logger logger : Logger instance.
        """
        pass

    def start(self):
        """Starts the test."""
        ontologies = [f for f in os.listdir(config.Paths.FUNC_DIR) if f.endswith('.owl')]
        logger = Logger(config.Paths.LOG)

        # Hello
        echo.pretty('Starting {} test on {} ontologies, this may take a while...'.format(self.name, len(ontologies)),
                    color=echo.Color.GREEN)

        # Setup/cleanup
        fileutils.create_dir(config.Paths.WRK_DIR)
        fileutils.create_dir(config.Paths.TEMP_DIR)
        fileutils.remove_dir_contents(config.Paths.TEMP_DIR)
        logger.clear()

        # Start test
        with logger:
            for onto_name in ontologies:
                func_ontology = Ontology(os.path.join(config.Paths.FUNC_DIR, onto_name))
                xml_ontology = Ontology(os.path.join(config.Paths.XML_DIR, onto_name))

                logger.log(onto_name, color=echo.Color.YELLOW, endl=False)
                logger.log(' (Functional: {} | RDFXML: {})'.format(func_ontology.readable_size,
                                                                   xml_ontology.readable_size))

                self.run(func_ontology, xml_ontology, logger)

                logger.log('')
