import re
from typing import Union

from src.pyutils import exc
from src.pyutils.proc import Benchmark, Task


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


class ResultsParser:
    """Parses reasoning task results."""

    # Public methods

    def parse_classification_results(self, task: Union[Task, Benchmark]) -> ReasoningStats:
        """Parse the results of the classification task."""
        return self._parse_reasoning_stats(task)

    def parse_consistency_results(self, task: Union[Task, Benchmark]) -> 'ConsistencyResults':
        """Parse the results of the consistency task."""
        stats = self._parse_reasoning_stats(task)

        result = re.search(r'The ontology is (.*)\.', task.stdout)
        exc.raise_if_falsy(result=result)
        consistent = (result.group(1) == 'consistent')

        return ConsistencyResults(consistent, stats)

    def parse_abduction_contraction_results(self, task: Union[Task, Benchmark]) -> 'AbductionContractionResults':
        """Parse the result of the abduction/contraction task by parsing stdout."""
        stdout = task.stdout
        exc.raise_if_falsy(stdout=stdout)

        res = re.search(r'Resource parsing: (.*) ms', stdout)
        exc.raise_if_falsy(res=res)
        res_parsing_ms = float(res.group(1))

        res = re.search(r'Request parsing: (.*) ms', stdout)
        exc.raise_if_falsy(res=res)
        req_parsing_ms = float(res.group(1))

        res = re.search(r'Reasoner initialization: (.*) ms', stdout)
        exc.raise_if_falsy(res=res)
        init_ms = float(res.group(1))

        res = re.search(r'Reasoning: (.*) ms', stdout)
        exc.raise_if_falsy(res=res)
        reasoning_ms = float(res.group(1))

        max_memory = self._parse_memory(task)

        return AbductionContractionResults(resource_parsing_ms=res_parsing_ms,
                                           request_parsing_ms=req_parsing_ms,
                                           init_ms=init_ms,
                                           reasoning_ms=reasoning_ms,
                                           max_memory=max_memory)

    # Protected methods

    def _parse_reasoning_stats(self, task: Union[Task, Benchmark]) -> ReasoningStats:
        """Parse stats for a reasoning task."""
        stdout = task.stdout
        exc.raise_if_falsy(stdout=stdout)

        res = re.search(r'Parsing: (.*) ms', stdout)
        exc.raise_if_falsy(res=res)
        parsing_ms = float(res.group(1))

        res = re.search(r'Reasoning: (.*) ms', stdout)
        exc.raise_if_falsy(res=res)
        reasoning_ms = float(res.group(1))

        max_memory = self._parse_memory(task)

        return ReasoningStats(parsing_ms=parsing_ms, reasoning_ms=reasoning_ms, max_memory=max_memory)

    def _parse_memory(self, task: Union[Task, Benchmark]) -> int:
        """Parse the peak memory for a reasoning task."""
        if isinstance(task, Benchmark):
            max_memory = task.max_memory
        else:
            res = re.search(r'Memory: (.*) B', task.stdout)
            max_memory = int(res.group(1)) if res else 0

        return max_memory
