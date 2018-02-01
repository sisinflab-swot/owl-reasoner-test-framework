import os
from abc import ABCMeta, abstractmethod
from typing import List, Optional

from src.pyutils import exc, fileutils
from .results import AbductionContractionResults, ConsistencyResults, ReasoningStats


class TestMode:
    """Test modes namespace."""
    CORRECTNESS = 'correctness'
    TIME = 'time'
    MEMORY = 'memory'
    MOBILE = 'mobile'

    ALL = [CORRECTNESS, TIME, MEMORY, MOBILE]


class OWLSyntax:
    """OWL ontology syntax namespace."""
    RDFXML = 'rdfxml'
    FUNCTIONAL = 'functional'

    ALL = [RDFXML, FUNCTIONAL]


class ReasoningTask:
    """Reasoning tasks namespace."""
    CLASSIFICATION = 'classification'
    CONSISTENCY = 'consistency'
    NON_STANDARD = 'non-standard'

    ALL = [CLASSIFICATION, CONSISTENCY, NON_STANDARD]


class OWLReasoner:
    """Abstract reasoner interface."""
    __metaclass__ = ABCMeta

    # Public properties

    @property
    @abstractmethod
    def name(self) -> str:
        """The display name of the reasoner."""
        pass

    @property
    @abstractmethod
    def supported_syntaxes(self) -> List[str]:
        """The OWL syntaxes supported by the reasoner."""
        pass

    @property
    @abstractmethod
    def preferred_syntax(self) -> str:
        """The default syntax used by the reasoner."""
        pass

    @property
    @abstractmethod
    def supported_tasks(self) -> List[str]:
        """Reasoning tasks supported by the reasoner."""
        pass

    @property
    def is_mobile(self) -> bool:
        """True if the class wraps a mobile reasoner, False otherwise."""
        return False

    # Public methods

    def __init__(self, path: str):
        """:param path : Path of the reasoner executable."""
        exc.raise_if_not_found(path, file_type=exc.FileType.FILE)
        self._path = path

    @abstractmethod
    def classify(self,
                 input_file: str,
                 output_file: Optional[str] = None,
                 timeout: Optional[float] = None,
                 mode: str = TestMode.CORRECTNESS) -> ReasoningStats:
        """Performs the classification reasoning task."""
        raise NotImplementedError

    @abstractmethod
    def consistency(self,
                    input_file: str,
                    timeout: Optional[float] = None,
                    mode: str = TestMode.CORRECTNESS) -> ConsistencyResults:
        """Checks if the given ontology is consistent."""
        raise NotImplementedError

    @abstractmethod
    def abduction_contraction(self,
                              resource_file: str,
                              request_file: str,
                              timeout: Optional[float] = None,
                              mode: str = TestMode.CORRECTNESS) -> AbductionContractionResults:
        """Performs abductions or contractions between all resource and request individuals."""
        raise NotImplementedError


class OWLOntology:
    """Models ontology files."""

    @property
    def name(self) -> str:
        """The file name of the ontology."""
        return os.path.basename(self.path)

    @property
    def size(self) -> int:
        """Size of the ontology in bytes."""
        return os.path.getsize(self.path)

    @property
    def readable_size(self) -> str:
        """Human readable string for the ontology size."""
        return fileutils.human_readable_size(self.path)

    def __init__(self, path: str, syntax: str):
        exc.raise_if_not_found(path, file_type=exc.FileType.FILE)
        self.path = path
        self.syntax = syntax
