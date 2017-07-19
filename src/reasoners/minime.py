import re
from os import path

from owl import AbductionContractionResults, ConsistencyResults, OWLReasoner, OWLSyntax, ReasoningStats, TestMode
from src.utils import bench, device, exc, fileutils, proc


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


class MiniMEMobile(OWLReasoner):
    """MiniME mobile reasoner wrapper."""

    # Lifecycle

    def __init__(self, project, scheme, classification_test, consistency_test):
        """
        :param str project : Test Xcode project.
        :param str scheme : Xcode project scheme.
        :param str classification_test : Name of the classification test.
        :param str consistency_test : Name of the consistency test.
        """
        exc.raise_if_not_found(project, file_type='dir')
        exc.raise_if_falsy(scheme=scheme, classification_test=classification_test, consistency_test=consistency_test)

        super(MiniMEMobile, self).__init__(path=proc.find_executable('xcodebuild'))
        self._project = project
        self._scheme = scheme
        self._classification_test = classification_test
        self._consistency_test = consistency_test

    # Overrides

    @property
    def name(self):
        return 'MiniME mobile'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML]

    @property
    def preferred_syntax(self):
        return OWLSyntax.RDFXML

    def classify(self, input_file, output_file=None, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type='file')

        args = self._args(test=self._classification_test, resource=input_file)
        result = proc.call(args, timeout=timeout)
        return extract_stats(result)

    def consistency(self, input_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type='file')

        args = self._args(test=self._consistency_test, resource=input_file)
        result = proc.call(args, timeout=timeout)
        return ConsistencyResults(consistent=True, stats=extract_stats(result))

    def abduction_contraction(self, resource_file, request_file, timeout=None, mode=TestMode.CORRECTNESS):
        pass

    # Private

    def _args(self, test, resource, request=None):
        """Builds the xcodebuild args for the specified test.

        :param str test : The test to run.
        :param str resource : The resource ontology.
        :param str request : The request ontology.
        :rtype : list[str]
        """
        args = [self._path,
                '-project', self._project,
                '-scheme', self._scheme,
                '-destination', 'platform=iOS,name={}'.format(device.detect_connected()),
                '-only-testing:{}'.format(test),
                'test-without-building',
                'RESOURCE={}'.format(path.splitext(path.basename(resource))[0])]

        if request:
            args.append('REQUEST={}'.format(path.splitext(path.basename(request))[0]))

        return args


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

    if isinstance(result, bench.BenchResult):
        max_memory = result.max_memory
    else:
        res = re.search(r'Memory: (.*) B', stdout)
        max_memory = long(res.group(1)) if res else 0

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
