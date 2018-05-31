import os
from abc import ABCMeta, abstractmethod
from typing import List, Optional

from src.pyutils import exc, fileutils
from src.pyutils.proc import Benchmark, Jar, OutputAction, Task
from .results import AbductionContractionResults, ConsistencyResults, ReasoningStats, ResultsParser


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


class MetaArgs:
    """Meta-arguments namespace."""
    INPUT = '<input_meta_arg>'
    OUTPUT = '<output_meta_arg>'
    REQUEST = '<request_meta_arg>'

    @staticmethod
    def replace(args: List[str], input_arg: str,
                output_arg: Optional[str] = None, request_arg: Optional[str] = None) -> List[str]:
        """Replace meta-args with actual ones."""
        replacements = {
            MetaArgs.INPUT: input_arg,
            MetaArgs.OUTPUT: output_arg,
            MetaArgs.REQUEST: request_arg
        }

        return [replacements.get(arg, arg) for arg in args]


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

    def __init__(self, path: str, owl_tool_path: Optional[str] = None, vm_opts: Optional[List[str]] = None):
        """:param path : Path of the reasoner executable."""
        exc.raise_if_not_found(path, file_type=exc.FileType.FILE)

        # Fields
        self.path = path
        self.owl_tool_path = owl_tool_path
        self.vm_opts = vm_opts
        self.results_parser = ResultsParser()

    @abstractmethod
    def args(self, task: str, mode: str) -> List[str]:
        """Args to be passed to the reasoner executable for each task and test mode."""
        raise NotImplementedError

    def classify(self,
                 input_file: str,
                 output_file: Optional[str] = None,
                 timeout: Optional[float] = None,
                 mode: str = TestMode.CORRECTNESS) -> ReasoningStats:
        """Performs the classification reasoning task."""
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)

        classification_out = None

        if output_file:
            classification_out = os.path.splitext(output_file)[0] + '.owl' if self.owl_tool_path else output_file
            fileutils.remove(output_file)
            fileutils.remove(classification_out)

        args = MetaArgs.replace(args=self.args(task=ReasoningTask.CLASSIFICATION, mode=mode),
                                input_arg=input_file,
                                output_arg=classification_out)

        task = self._run(args=args, timeout=timeout, mode=mode)

        if mode == TestMode.CORRECTNESS and self.owl_tool_path:
            exc.raise_if_not_found(self.owl_tool_path, file_type=exc.FileType.FILE)
            args = ['print-tbox', '-o', output_file, classification_out]
            jar = Jar(self.owl_tool_path, jar_args=args, vm_opts=self.vm_opts, output_action=OutputAction.DISCARD)
            jar.run()

        return self.results_parser.parse_classification_results(task)

    def consistency(self,
                    input_file: str,
                    timeout: Optional[float] = None,
                    mode: str = TestMode.CORRECTNESS) -> ConsistencyResults:
        """Checks if the given ontology is consistent."""
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)

        args = MetaArgs.replace(args=self.args(task=ReasoningTask.CONSISTENCY, mode=mode),
                                input_arg=input_file)

        task = self._run(args, timeout=timeout, mode=mode)
        return self.results_parser.parse_consistency_results(task)

    def abduction_contraction(self,
                              resource_file: str,
                              request_file: str,
                              timeout: Optional[float] = None,
                              mode: str = TestMode.CORRECTNESS) -> AbductionContractionResults:
        """Performs abductions or contractions between all resource and request individuals."""
        exc.raise_if_not_found(resource_file, file_type=exc.FileType.FILE)
        exc.raise_if_not_found(request_file, file_type=exc.FileType.FILE)

        args = MetaArgs.replace(args=self.args(task=ReasoningTask.NON_STANDARD, mode=mode),
                                input_arg=resource_file,
                                request_arg=request_file)

        task = self._run(args, timeout=timeout, mode=mode)
        return self.results_parser.parse_abduction_contraction_results(task)

    # Protected methods

    def _run(self, args: List[str], timeout: Optional[float], mode: str) -> Task:
        """Runs the reasoner."""
        task = Task(self.path, args=args)

        if mode == TestMode.MEMORY:
            task = Benchmark(task)

        task.run(timeout=timeout)
        return task


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
