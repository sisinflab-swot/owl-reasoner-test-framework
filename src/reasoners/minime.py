import errno
import re
from os import path
from typing import List, Optional, Union

from src.pyutils import exc, fileutils
from src.pyutils.proc import Benchmark, Task, find_executable
from .owl import AbductionContractionResults, ConsistencyResults, OWLReasoner, OWLSyntax, ReasoningStats, TestMode


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
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)

        args = ['classification', '-i', input_file]

        if mode == TestMode.CORRECTNESS:
            fileutils.remove(output_file)
            args.extend(['-o', output_file])

        result = self._run(args, timeout=timeout, mode=mode)

        return extract_stats(result)

    def consistency(self, input_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)

        args = ['consistency', '-i', input_file]
        result = self._run(args, timeout=timeout, mode=mode)
        return extract_consistency_results(result)

    def abduction_contraction(self, resource_file, request_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(resource_file, file_type=exc.FileType.FILE)
        exc.raise_if_not_found(request_file, file_type=exc.FileType.FILE)

        args = ['abduction-contraction', '-i', resource_file, '-r', request_file]
        result = self._run(args, timeout=timeout, mode=mode)
        return extract_abduction_contraction_results(result)

    # Private methods

    def _run(self, args: List[str], timeout: Optional[float], mode: str) -> Union[Task, Benchmark]:
        result = Task(self._path, args=args)

        if mode == TestMode.MEMORY:
            result = Benchmark(result)

        result.run(timeout=timeout)
        return result


class MiniMEMobile(OWLReasoner):
    """MiniME mobile reasoner wrapper."""

    # Lifecycle

    def __init__(self,
                 project: str,
                 scheme: str,
                 classification_test: str,
                 consistency_test: str,
                 abduction_contraction_test: str):
        """
        :param project : Test Xcode project.
        :param scheme : Xcode project scheme.
        :param classification_test : Name of the classification test.
        :param consistency_test : Name of the consistency test.
        :param abduction_contraction_test : Name of the abduction/contraction test.
        """
        exc.raise_if_not_found(project, file_type=exc.FileType.DIR)
        exc.raise_if_falsy(scheme=scheme, classification_test=classification_test, consistency_test=consistency_test)

        super(MiniMEMobile, self).__init__(path=find_executable('xcodebuild'))
        self._project = project
        self._scheme = scheme
        self._classification_test = classification_test
        self._consistency_test = consistency_test
        self._abduction_contraction_test = abduction_contraction_test

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
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)
        result = self._run(test=self._classification_test, resource=input_file, timeout=timeout)
        return extract_stats(result)

    def consistency(self, input_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)
        result = self._run(test=self._consistency_test, resource=input_file, timeout=timeout)
        return ConsistencyResults(consistent=True, stats=extract_stats(result))

    def abduction_contraction(self, resource_file, request_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(resource_file, file_type=exc.FileType.FILE)
        exc.raise_if_not_found(request_file, file_type=exc.FileType.FILE)

        result = self._run(test=self._abduction_contraction_test,
                           resource=resource_file,
                           request=request_file,
                           timeout=timeout)

        return extract_abduction_contraction_results(result)

    # Private

    def _run(self, test: str, resource: str, timeout: Optional[float], request: Optional[str] = None) -> Task:
        args = ['-project', self._project,
                '-scheme', self._scheme,
                '-destination', 'platform=iOS,name={}'.format(self._detect_connected_device()),
                '-only-testing:{}'.format(test),
                'test-without-building',
                'RESOURCE={}'.format(path.splitext(path.basename(resource))[0])]

        if request:
            args.append('REQUEST={}'.format(path.splitext(path.basename(request))[0]))

        task = Task(self._path, args=args)
        task.run(timeout=timeout)

        return task

    def _detect_connected_device(self) -> str:
        """Returns the name of a connected device."""
        task = Task('instruments', args=['-s', 'devices'])
        task.run()

        for line in task.stdout.splitlines():
            components = line.split(' (', 1)

            if len(components) == 2 and not components[1].endswith('(Simulator)'):
                return components[0]

        exc.raise_ioerror(errno.ENODEV, message='No connected devices.')


# Utility functions


def extract_memory(result: Union[Task, Benchmark]) -> int:
    """Extracts the peak memory for a reasoning task."""
    if isinstance(result, Benchmark):
        max_memory = result.max_memory
    else:
        res = re.search(r'Memory: (.*) B', result.stdout)
        max_memory = int(res.group(1)) if res else 0

    return max_memory


def extract_stats(result: Union[Task, Benchmark]) -> ReasoningStats:
    """Extract stats for a reasoning task."""
    stdout = result.stdout
    exc.raise_if_falsy(stdout=stdout)

    res = re.search(r'Parsing: (.*) ms', stdout)
    exc.raise_if_falsy(res=res)
    parsing_ms = float(res.group(1))

    res = re.search(r'Reasoning: (.*) ms', stdout)
    exc.raise_if_falsy(res=res)
    reasoning_ms = float(res.group(1))

    max_memory = extract_memory(result)

    return ReasoningStats(parsing_ms=parsing_ms, reasoning_ms=reasoning_ms, max_memory=max_memory)


def extract_consistency_results(result: Union[Task, Benchmark]) -> ConsistencyResults:
    """Extract the results of the consistency task."""
    stats = extract_stats(result)

    result = re.search(r'The ontology is (.*)\.', result.stdout)
    exc.raise_if_falsy(result=result)
    consistent = (result.group(1) == 'consistent')

    return ConsistencyResults(consistent, stats)


def extract_abduction_contraction_results(result) -> AbductionContractionResults:
    """Extract the result of the abduction/contraction task by parsing stdout."""
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

    max_memory = extract_memory(result)

    return AbductionContractionResults(resource_parsing_ms=res_parsing_ms,
                                       request_parsing_ms=req_parsing_ms,
                                       init_ms=init_ms,
                                       reasoning_ms=reasoning_ms,
                                       max_memory=max_memory)
