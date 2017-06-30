import re

from owl import AbductionContractionResults, ConsistencyResults, OWLReasoner, OWLSyntax, ReasoningStats, TestMode
from src.utils import bench, exc, fileutils, proc


class MiniME(OWLReasoner):
    """MiniME reasoner wrapper."""

    # Overrides

    @property
    def name(self):
        return 'MiniME'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML]

    @property
    def preferred_syntax(self):
        return OWLSyntax.RDFXML

    def classify(self, input_file, output_file=None, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type='file')

        args = [self._path, 'classification', '-i', input_file]

        if mode == TestMode.CORRECTNESS:
            fileutils.remove(output_file)
            args.extend(['-o', output_file])

        if mode == TestMode.MEMORY:
            result = bench.benchmark(args, timeout=timeout)
        else:
            result = proc.call(args, timeout=timeout)

        return extract_stats(result)

    def consistency(self, input_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type='file')

        args = [self._path, 'consistency', '-i', input_file]

        if mode == TestMode.MEMORY:
            result = bench.benchmark(args, timeout=timeout)
        else:
            result = proc.call(args, timeout=timeout)

        return extract_consistency_results(result)

    def abduction_contraction(self, resource_file, request_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(resource_file, file_type='file')
        exc.raise_if_not_found(request_file, file_type='file')

        args = [self._path, 'abduction-contraction', '-i', resource_file, '-r', request_file]

        if mode == TestMode.MEMORY:
            result = bench.benchmark(args, timeout=timeout)
        else:
            result = proc.call(args, timeout=timeout)

        return extract_abduction_contraction_results(result)


# Utility functions


def extract_stats(result):
    """Extract stats for a reasoning task.

    :param proc.CallResult result : CallResult instance.
    :rtype : Stats
    """
    stdout = result.stdout
    exc.raise_if_falsy(stdout=stdout)

    res = re.search(r'Parsing: (.*) ms', stdout)
    exc.raise_if_falsy(res=res)
    parsing_ms = float(res.group(1))

    res = re.search(r'Reasoning: (.*) ms', stdout)
    exc.raise_if_falsy(res=res)
    reasoning_ms = float(res.group(1))

    max_memory = result.max_memory if isinstance(result, bench.BenchResult) else 0

    return ReasoningStats(parsing_ms=parsing_ms, reasoning_ms=reasoning_ms, max_memory=max_memory)


def extract_consistency_results(result):
    """Extract the results of the consistency task.

    :param proc.CallResult result : CallResult instance.
    :rtype : ConsistencyResults
    """
    stats = extract_stats(result)

    result = re.search(r'The ontology is (.*)\.', result.stdout)
    exc.raise_if_falsy(result=result)
    consistent = (result.group(1) == 'consistent')

    return ConsistencyResults(consistent, stats)


def extract_abduction_contraction_results(result):
    """Extract the result of the abduction/contraction task by parsing stdout.

    :param proc.CallResult result : CallResult instance.
    :rtype : AbductionContractionResults
    """
    stdout = result.stdout
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

    max_memory = result.max_memory if isinstance(result, bench.BenchResult) else 0

    return AbductionContractionResults(resource_parsing_ms=res_parsing_ms,
                                       request_parsing_ms=req_parsing_ms,
                                       init_ms=init_ms,
                                       reasoning_ms=reasoning_ms,
                                       max_memory=max_memory)
