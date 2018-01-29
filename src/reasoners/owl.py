import os
from abc import ABCMeta, abstractmethod
from typing import List, Optional

from src.pyutils import exc, fileutils


class TestMode:
    """Test mode pseudo-enum."""
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


class ReasoningStats:
    """Contains stats about a reasoning task."""

    def __init__(self, parsing_ms: float = 0.0, reasoning_ms: float = 0.0, max_memory: int = 0):
        self.parsing_ms = parsing_ms
        self.reasoning_ms = reasoning_ms
        self.max_memory = max_memory


class ConsistencyResults:
    """Contains results for the consistency task."""

    def __init__(self, consistent: bool, stats: ReasoningStats):
        self.consistent = consistent
        self.stats = stats


class AbductionContractionResults(object):
    """Contains results for the abduction-contraction task."""

    def __init__(self,
                 resource_parsing_ms: float = 0.0,
                 request_parsing_ms: float = 0.0,
                 init_ms: float = 0.0,
                 reasoning_ms: float = 0.0,
                 max_memory: int = 0):
        self.resource_parsing_ms = resource_parsing_ms
        self.request_parsing_ms = request_parsing_ms
        self.init_ms = init_ms
        self.reasoning_ms = reasoning_ms
        self.max_memory = max_memory


class OWLReasoner:
    """Abstract reasoner interface."""
    __metaclass__ = ABCMeta

    # Public properties

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def supported_syntaxes(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def preferred_syntax(self) -> str:
        pass

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
        return os.path.basename(self.path)

    @property
    def size(self) -> int:
        return os.path.getsize(self.path)

    @property
    def readable_size(self) -> str:
        return fileutils.human_readable_size(self.path)

    def __init__(self, path: str, syntax: str):
        exc.raise_if_not_found(path, file_type=exc.FileType.FILE)
        self.path = path
        self.syntax = syntax
