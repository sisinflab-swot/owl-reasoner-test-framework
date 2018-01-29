import re
import os
from typing import List, Optional, Union

from src.pyutils import exc, fileutils
from src.pyutils.proc import Benchmark, Jar, OutputAction, Task
from .owl import ConsistencyResults, OWLReasoner, OWLSyntax, ReasoningStats, TestMode


class Konclude(OWLReasoner):
    """Konclude reasoner wrapper."""

    # Public methods

    def __init__(self, path: str, owl_tool_path: str, vm_opts: List[str]):
        super(Konclude, self).__init__(path)
        exc.raise_if_not_found(owl_tool_path, file_type=exc.FileType.FILE)
        self.__owl_tool_path = owl_tool_path
        self.__vm_opts = vm_opts

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

    def classify(self, input_file, output_file=None, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)

        args = ['classification', '-i', input_file]
        classification_out = None

        if mode == TestMode.CORRECTNESS:
            classification_out = os.path.splitext(output_file)[0] + '.owl'

            fileutils.remove(output_file)
            fileutils.remove(classification_out)

            args.extend(['-o', classification_out])

        args.append('-v')

        result = self._run(args=args, timeout=timeout, mode=mode)

        if mode == TestMode.CORRECTNESS:
            args = ['print-tbox', '-o', output_file, classification_out]
            jar = Jar(self.__owl_tool_path, jar_args=args, vm_opts=self.__vm_opts, output_action=OutputAction.DISCARD)
            jar.run()

        return self._extract_classification_stats(result)

    def consistency(self, input_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)

        args = ['consistency', '-i', input_file, '-v']
        result = self._run(args=args, timeout=timeout, mode=mode)

        return self._extract_consistency_results(result)

    def abduction_contraction(self, resource_file, request_file, timeout=None, mode=TestMode.CORRECTNESS):
        raise NotImplementedError

    # Private methods

    def _run(self, args: List[str], timeout: Optional[float], mode: str) -> Task:
        task = Task(self._path, args=args)

        if mode == TestMode.MEMORY:
            task = Benchmark(task)

        task.run(timeout=timeout)
        return task

    def _extract_stats(self, result: Union[Task, Benchmark]) -> ReasoningStats:
        stdout = result.stdout
        exc.raise_if_falsy(stdout=stdout)

        res = re.search(r'>> Ontology parsed in (.*) ms\.', stdout)
        exc.raise_if_falsy(res=res)
        parsing_ms = float(res.group(1))

        res = re.search(r'Total processing time: (.*) ms\.', stdout)
        exc.raise_if_falsy(res=res)
        total_ms = float(res.group(1))

        max_memory = result.max_memory if isinstance(result, Benchmark) else 0

        return ReasoningStats(parsing_ms=parsing_ms, reasoning_ms=(total_ms - parsing_ms), max_memory=max_memory)

    def _extract_classification_stats(self, result: Union[Task, Benchmark]) -> ReasoningStats:
        stats = self._extract_stats(result)

        res = re.search(r'Query \'UnnamedWriteClassHierarchyQuery\' processed in \'(.*)\' ms\.', result.stdout)

        if res:
            write_ms = float(res.group(1))
            stats.reasoning_ms -= write_ms

        return stats

    def _extract_consistency_results(self, result: Union[Task, Benchmark]) -> ConsistencyResults:
        stats = self._extract_stats(result)

        res = re.search(r'Ontology \'.*\' is (.*)\.', result.stdout)
        exc.raise_if_falsy(res=res)
        consistent = (res.group(1) == 'consistent')

        return ConsistencyResults(consistent, stats)
