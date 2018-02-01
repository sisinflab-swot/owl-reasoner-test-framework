import errno
import os
from typing import List, Optional, Union

from src.pyutils import exc, fileutils
from src.pyutils.proc import Benchmark, Task, find_executable
from .java import JavaReasoner
from .owl import (
    OWLReasoner,
    OWLSyntax,
    ReasoningTask,
    TestMode
)
from .results import AbductionContractionResults, ConsistencyResults, ReasoningStats


class MiniMEJava(JavaReasoner):
    """MiniME Java reasoner wrapper."""

    # Public methods

    def __init__(self, path: str, owl_tool_path: str, vm_opts: List[str]):
        super(MiniMEJava, self).__init__(name='MiniME Java', path=path, owl_tool_path=owl_tool_path, vm_opts=vm_opts)

    # Overrides

    @property
    def supported_tasks(self):
        return [ReasoningTask.CLASSIFICATION, ReasoningTask.CONSISTENCY, ReasoningTask.NON_STANDARD]

    def abduction_contraction(self, resource_file, request_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(resource_file, file_type=exc.FileType.FILE)
        exc.raise_if_not_found(request_file, file_type=exc.FileType.FILE)

        args = ['abduction-contraction', '-r', request_file, resource_file]
        task = self._run(args, timeout=timeout, mode=mode)

        return AbductionContractionResults.extract(task)


class MiniMESwift(OWLReasoner):
    """MiniME Swift reasoner wrapper."""

    # Overrides

    @property
    def name(self):
        return 'MiniME Swift'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML]

    @property
    def preferred_syntax(self):
        return OWLSyntax.RDFXML

    @property
    def supported_tasks(self):
        return [ReasoningTask.CLASSIFICATION, ReasoningTask.CONSISTENCY, ReasoningTask.NON_STANDARD]

    def classify(self, input_file, output_file=None, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)

        args = ['classification', '-i', input_file]

        if mode == TestMode.CORRECTNESS:
            fileutils.remove(output_file)
            args.extend(['-o', output_file])

        task = self._run(args, timeout=timeout, mode=mode)

        return ReasoningStats.extract(task)

    def consistency(self, input_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)

        args = ['consistency', '-i', input_file]
        task = self._run(args, timeout=timeout, mode=mode)
        return ConsistencyResults.extract(task)

    def abduction_contraction(self, resource_file, request_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(resource_file, file_type=exc.FileType.FILE)
        exc.raise_if_not_found(request_file, file_type=exc.FileType.FILE)

        args = ['abduction-contraction', '-i', resource_file, '-r', request_file]
        task = self._run(args, timeout=timeout, mode=mode)
        return AbductionContractionResults.extract(task)

    # Private methods

    def _run(self, args: List[str], timeout: Optional[float], mode: str) -> Union[Task, Benchmark]:
        result = Task(self._path, args=args)

        if mode == TestMode.MEMORY:
            result = Benchmark(result)

        result.run(timeout=timeout)
        return result


class MiniMESwiftMobile(OWLReasoner):
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

        super(MiniMESwiftMobile, self).__init__(path=find_executable('xcodebuild'))
        self._project = project
        self._scheme = scheme
        self._classification_test = classification_test
        self._consistency_test = consistency_test
        self._abduction_contraction_test = abduction_contraction_test

    # Overrides

    @property
    def name(self):
        return 'MiniME Swift mobile'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML]

    @property
    def preferred_syntax(self):
        return OWLSyntax.RDFXML

    @property
    def supported_tasks(self):
        return [ReasoningTask.CLASSIFICATION, ReasoningTask.CONSISTENCY, ReasoningTask.NON_STANDARD]

    @property
    def is_mobile(self):
        return True

    def classify(self, input_file, output_file=None, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)
        task = self._run(test=self._classification_test, resource=input_file, timeout=timeout)
        return ReasoningStats.extract(task)

    def consistency(self, input_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)
        task = self._run(test=self._consistency_test, resource=input_file, timeout=timeout)
        return ConsistencyResults(consistent=True, stats=ReasoningStats.extract(task))

    def abduction_contraction(self, resource_file, request_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(resource_file, file_type=exc.FileType.FILE)
        exc.raise_if_not_found(request_file, file_type=exc.FileType.FILE)

        task = self._run(test=self._abduction_contraction_test,
                         resource=resource_file,
                         request=request_file,
                         timeout=timeout)

        return AbductionContractionResults.extract(task)

    # Private

    def _run(self, test: str, resource: str, timeout: Optional[float], request: Optional[str] = None) -> Task:
        args = ['-project', self._project,
                '-scheme', self._scheme,
                '-destination', 'platform=iOS,name={}'.format(self._detect_connected_device()),
                '-only-testing:{}'.format(test),
                'test-without-building',
                'RESOURCE={}'.format(os.path.splitext(os.path.basename(resource))[0])]

        if request:
            args.append('REQUEST={}'.format(os.path.splitext(os.path.basename(request))[0]))

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
