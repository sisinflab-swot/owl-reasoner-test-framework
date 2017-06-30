import re
import os

from owl import ConsistencyResults, OWLReasoner, OWLSyntax, ReasoningStats, TestMode
from src.utils import bench, exc, fileutils, jar, proc


class Konclude(OWLReasoner):
    """Konclude reasoner wrapper."""

    # Public methods

    def __init__(self, path, owl_tool_path, vm_opts):
        """
        :param str path : Path of the Konclude executable.
        :param str owl_tool_path : Path of the owltool jar.
        :param list[str] vm_opts : Options for the Java VM.
        """
        super(Konclude, self).__init__(path)
        exc.raise_if_not_found(owl_tool_path, file_type='file')
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
        exc.raise_if_not_found(input_file, file_type='file')

        args = [self._path, 'classification', '-i', input_file]
        classification_out = None

        if mode == TestMode.CORRECTNESS:
            classification_out = os.path.splitext(output_file)[0] + '.owl'

            fileutils.remove(output_file)
            fileutils.remove(classification_out)

            args.extend(['-o', classification_out])

        args.append('-v')

        if mode == TestMode.MEMORY:
            result = bench.benchmark(args, timeout=timeout)
        else:
            result = proc.call(args, timeout=timeout)

        if mode == TestMode.CORRECTNESS:
            args = ['print-tbox', '-o', output_file, classification_out]
            jar.call(self.__owl_tool_path,
                     args=args,
                     vm_opts=self.__vm_opts,
                     output_action=proc.OutputAction.DISCARD)

        return self.__extract_classification_stats(result)

    def consistency(self, input_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type='file')

        args = [self._path, 'consistency', '-i', input_file, '-v']

        if mode == TestMode.MEMORY:
            result = bench.benchmark(args, timeout=timeout)
        else:
            result = proc.call(args, timeout=timeout)

        return self.__extract_consistency_results(result)

    def abduction_contraction(self, resource_file, request_file, timeout=None, mode=TestMode.CORRECTNESS):
        raise NotImplementedError

    # Private methods

    def __extract_stats(self, result):
        """Extract stats for a reasoning task.

        :param proc.CallResult result : CallResult instance.
        :rtype : Stats
        """
        stdout = result.stdout
        exc.raise_if_falsy(stdout=stdout)

        res = re.search(r'>> Ontology parsed in (.*) ms\.', stdout)
        exc.raise_if_falsy(res=res)
        parsing_ms = float(res.group(1))

        res = re.search(r'Total processing time: (.*) ms\.', stdout)
        exc.raise_if_falsy(res=res)
        total_ms = float(res.group(1))

        max_memory = result.max_memory if isinstance(result, bench.BenchResult) else 0

        return ReasoningStats(parsing_ms=parsing_ms, reasoning_ms=(total_ms - parsing_ms), max_memory=max_memory)

    def __extract_classification_stats(self, result):
        """Extract stats for the classification task.

        :param proc.CallResult result : CallResult instance.
        :rtype : Stats
        """
        stats = self.__extract_stats(result)

        res = re.search(r'Query \'UnnamedWriteClassHierarchyQuery\' processed in \'(.*)\' ms\.', result.stdout)

        if res:
            write_ms = float(res.group(1))
            stats.reasoning_ms -= write_ms

        return stats

    def __extract_consistency_results(self, result):
        """Extract the result of the consistency task.

        :param proc.CallResult result : CallResult instance.
        :rtype : ConsistencyResults
        """
        stats = self.__extract_stats(result)

        res = re.search(r'Ontology \'.*\' is (.*)\.', result.stdout)
        exc.raise_if_falsy(res=res)
        consistent = (res.group(1) == 'consistent')

        return ConsistencyResults(consistent, stats)
