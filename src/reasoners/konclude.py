import re
from typing import List, Union

from src.pyutils import exc
from src.pyutils.proc import Benchmark, Task
from .owl import (
    MetaArgs,
    OWLReasoner,
    OWLSyntax,
    ReasoningTask,
    TestMode
)
from .results import ConsistencyResults, ReasoningStats, ResultsParser


class KoncludeResultsParser(ResultsParser):
    """Parser for Konclude results."""

    def parse_classification_results(self, task: Union[Task, Benchmark]) -> ReasoningStats:
        stats = self._parse_reasoning_stats(task)

        res = re.search(r'Query \'UnnamedWriteClassHierarchyQuery\' processed in \'(.*)\' ms\.', task.stdout)

        if res:
            write_ms = float(res.group(1))
            stats.reasoning_ms -= write_ms

        return stats

    def parse_consistency_results(self, task: Union[Task, Benchmark]) -> ConsistencyResults:
        stats = self._parse_reasoning_stats(task)

        res = re.search(r'Ontology \'.*\' is (.*)\.', task.stdout)
        exc.raise_if_falsy(res=res)
        consistent = (res.group(1) == 'consistent')

        return ConsistencyResults(consistent, stats)

    def _parse_reasoning_stats(self, task: Union[Task, Benchmark]) -> ReasoningStats:
        stdout = task.stdout
        exc.raise_if_falsy(stdout=stdout)

        res = re.search(r'>> Ontology parsed in (.*) ms\.', stdout)
        exc.raise_if_falsy(res=res)
        parsing_ms = float(res.group(1))

        res = re.search(r'Total processing time: (.*) ms\.', stdout)
        exc.raise_if_falsy(res=res)
        total_ms = float(res.group(1))

        max_memory = self._parse_memory(task)

        return ReasoningStats(parsing_ms=parsing_ms, reasoning_ms=(total_ms - parsing_ms), max_memory=max_memory)


class Konclude(OWLReasoner):
    """Konclude reasoner wrapper."""

    # Overrides

    @property
    def name(self):
        return 'Konclude'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.FUNCTIONAL]

    @property
    def preferred_syntax(self):
        return OWLSyntax.FUNCTIONAL

    @property
    def supported_tasks(self):
        return [ReasoningTask.CLASSIFICATION, ReasoningTask.CONSISTENCY]

    def args(self, task: str, mode: str) -> List[str]:
        if task == ReasoningTask.CLASSIFICATION:
            args = ['classification', '-i', MetaArgs.INPUT]
            if mode == TestMode.CORRECTNESS:
                args.extend(['-o', MetaArgs.OUTPUT])
            args.append('-v')
        elif task == ReasoningTask.CONSISTENCY:
            args = ['consistency', '-i', MetaArgs.INPUT, '-v']
        else:
            args = []

        return args

    def __init__(self, path: str, owl_tool_path: str, vm_opts: List[str]) -> None:
        super(Konclude, self).__init__(path, owl_tool_path, vm_opts)
        self.results_parser = KoncludeResultsParser()
