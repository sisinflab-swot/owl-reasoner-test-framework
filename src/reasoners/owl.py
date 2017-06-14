import os
from abc import ABCMeta, abstractmethod, abstractproperty

from src.utils import exc, fileutils


class OWLReasoner(object):
    """Abstract reasoner interface."""
    __metaclass__ = ABCMeta

    # Public properties

    @abstractproperty
    def name(self):
        """:rtype : str"""
        pass

    @abstractproperty
    def supported_syntaxes(self):
        """:rtype : list[str]"""
        pass

    @abstractproperty
    def preferred_syntax(self):
        """:rtype : str"""
        pass

    # Public methods

    def __init__(self, path):
        """:param str path : Path of the reasoner executable."""
        exc.raise_if_not_found(path, file_type='file')
        self._path = path

    @abstractmethod
    def classify(self, input_file, output_file=None, timeout=None):
        """Performs the classification reasoning task.

        :param str input_file : Path of the input ontology.
        :param str output_file : Path of the output file.
        :param float timeout : Timeout (s).
        :rtype : Stats
        :return : Stats for the classification task.
        """
        raise NotImplementedError

    @abstractmethod
    def consistency(self, input_file, timeout=None):
        """Checks if the given ontology is consistent.

        :param str input_file : Path of the input ontology.
        :param float timeout : Timeout (s).
        :param float timeout : Timeout (s).
        :rtype : ConsistencyResults
        :return Results for the consistency task.
        """
        raise NotImplementedError

    @abstractmethod
    def abduction_contraction(self, resource_file, request_file, timeout=None):
        """Performs abductions or contractions between all resource and request individuals.

        :param str resource_file : Path of the resource ontology.
        :param str request_file : Path of the request ontology.
        :param float timeout : Timeout (s).
        :rtype : AbductionContractionResults
        :return : Results for the reasoning task.
        """
        raise NotImplementedError


class OWLOntology(object):
    """Models ontology files."""

    @property
    def name(self):
        """:rtype : str"""
        return os.path.basename(self.path)

    @property
    def readable_size(self):
        """:rtype : str"""
        return fileutils.human_readable_size(self.path)

    def __init__(self, path, syntax):
        """
        :param str path : The path of the ontology.
        :param str syntax : The syntax of the ontology.
        """
        exc.raise_if_not_found(path, file_type='file')
        self.path = path
        self.syntax = syntax


class OWLSyntax(object):
    """OWL ontology syntax namespace."""
    RDFXML = 'rdfxml'
    FUNCTIONAL = 'functional'


class ReasoningStats(object):
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


class ConsistencyResults(object):
    """Contains results for the consistency task."""
    def __init__(self, consistent, stats):
        """
        :param bool consistent : True if the ontology is consistent, False otherwise.
        :param ReasoningStats stats : Stats for the consistency task.
        """
        self.consistent = consistent
        self.stats = stats


class AbductionContractionResults(object):
    """Contains results for the abduction-contraction task."""

    def __init__(self, resource_parsing_ms=0.0, request_parsing_ms=0.0, init_ms=0.0, reasoning_ms=0.0, error=None):
        """
        :param float resource_parsing_ms : Resource parsing time in ms.
        :param float request_parsing_ms : Request parsing time in ms.
        :param float init_ms : Reasoner init time in ms.
        :param float reasoning_ms : Reasoning time in ms.
        :param str error : Error message.
        """
        self.resource_parsing_ms = resource_parsing_ms
        self.request_parsing_ms = request_parsing_ms
        self.init_ms = init_ms
        self.reasoning_ms = reasoning_ms
        self.error = error
