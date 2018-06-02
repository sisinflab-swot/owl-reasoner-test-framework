import re
from typing import List, Union

from src.pyutils import exc
from src.pyutils.proc import Benchmark, Task
from .java import JavaReasoner
from .owl import (
    MetaArgs,
    OWLReasoner,
    OWLSyntax,
    ReasoningTask,
    TestMode
)
from .results import ConsistencyResults, ResultsParser


class MiniMEObjC3(OWLReasoner):
    """Mini-ME Objective-C 3.0 reasoner wrapper."""

    @property
    def name(self):
        return 'Mini-ME ObjC 3.0'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML]

    @property
    def preferred_syntax(self):
        return OWLSyntax.RDFXML

    @property
    def supported_tasks(self):
        return [ReasoningTask.CLASSIFICATION, ReasoningTask.CONSISTENCY, ReasoningTask.NON_STANDARD]

    def __init__(self, path: str):
        super(MiniMEObjC3, self).__init__(path=path, owl_tool_path=None, vm_opts=None)
        self.results_parser = MiniME3ResultsParser()

    def args(self, task: str, mode: str) -> List[str]:
        return _get_args(task=task, mode=mode)


class MiniMEJava3(JavaReasoner):
    """MiniME Java 3.0 reasoner wrapper."""

    @property
    def supported_tasks(self):
        return [ReasoningTask.CLASSIFICATION, ReasoningTask.CONSISTENCY, ReasoningTask.NON_STANDARD]

    def __init__(self, path: str, vm_opts: List[str]):
        super(MiniMEJava3, self).__init__(name='Mini-ME Java 3.0', path=path,
                                          owl_tool_path=None, vm_opts=vm_opts)
        self.results_parser = MiniME3ResultsParser()

    def args(self, task: str, mode: str) -> List[str]:
        return _get_args(task=task, mode=mode)


# Private


def _get_args(task: str, mode: str) -> List[str]:
    """'args' method implementation for Mini-ME 3.0."""
    if task == ReasoningTask.CLASSIFICATION:
        args = ['classification', '-i', MetaArgs.INPUT]

        if mode == TestMode.CORRECTNESS:
            args.extend(['-o', MetaArgs.OUTPUT])
    elif task == ReasoningTask.CONSISTENCY:
        args = ['coherence', '-i', MetaArgs.INPUT]
    else:
        args = ['abduction-contraction', '-i', MetaArgs.INPUT, '-r', MetaArgs.REQUEST]

    if mode != TestMode.CORRECTNESS:
        args.append('-q')

    args.append('-b')

    return args


class MiniME3ResultsParser(ResultsParser):
    """Parser for Mini-ME 3.0 results."""

    def parse_consistency_results(self, task: Union[Task, Benchmark]) -> ConsistencyResults:
        stats = self._parse_reasoning_stats(task)

        result = re.search(r'The ontology is (.*)\.', task.stdout)
        exc.raise_if_falsy(result=result)
        consistent = (result.group(1) == 'coherent')

        return ConsistencyResults(consistent, stats)
