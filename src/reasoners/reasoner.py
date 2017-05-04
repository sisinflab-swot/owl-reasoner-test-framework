from abc import ABCMeta, abstractmethod, abstractproperty
from src.utils import exc


class Reasoner(object):
    """Abstract reasoner wrapper."""
    __metaclass__ = ABCMeta

    # Public properties

    @abstractproperty
    def name(self):
        """:rtype : str"""
        pass

    # Public methods

    def __init__(self, path):
        """:param str path : Path of the reasoner executable."""
        exc.raise_if_not_found(path, file_type='file')
        self._path = path

    @abstractmethod
    def classify(self, input_file, output_file=None):
        """Performs the classification reasoning task.

        :param str input_file : Path of the input ontology.
        :param str output_file : Path of the output file.
        :rtype : Stats
        :return : Stats for the classification task.
        """
        pass


class Stats(object):
    """Contains stats about a reasoning task."""

    def __init__(self, parsing_ms=0.0, reasoning_ms=0.0, error=None):
        """
        :param float parsing_ms : Parsing time in ms.
        :param float reasoning_ms : Reasoning time in ms.
        :param str error : Error message.
        """
        self.parsing_ms = parsing_ms
        self.reasoning_ms = reasoning_ms
        self.error = error
