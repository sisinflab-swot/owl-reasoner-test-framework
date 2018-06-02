import errno
import os
from typing import List, Optional

from src.pyutils import exc
from src.pyutils.proc import Task, find_executable
from .java import JavaReasoner
from .owl import (
    MetaArgs,
    OWLReasoner,
    OWLSyntax,
    ReasoningTask,
    TestMode
)
from .results import ConsistencyResults


class MiniMEJava2(JavaReasoner):
    """MiniME Java 2.0 reasoner wrapper."""

    @property
    def supported_tasks(self):
        return ReasoningTask.ALL

    def __init__(self, path: str, owl_tool_path: str, vm_opts: List[str]):
        super(MiniMEJava2, self).__init__(name='Mini-ME Java 2.0', path=path,
                                          owl_tool_path=owl_tool_path, vm_opts=vm_opts)

    def args(self, task: str, mode: str) -> List[str]:
        if task == ReasoningTask.NON_STANDARD:
            return ['abduction-contraction', '-r', MetaArgs.REQUEST, MetaArgs.INPUT]
        else:
            return super(MiniMEJava2, self).args(task, mode)


class MiniMESwift(OWLReasoner):
    """MiniME Swift reasoner wrapper."""

    @property
    def name(self):
        return 'Mini-ME Swift'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML]

    @property
    def supported_tasks(self):
        return ReasoningTask.ALL

    def args(self, task: str, mode: str) -> List[str]:
        if task == ReasoningTask.CLASSIFICATION:
            args = ['classification', '-i', MetaArgs.INPUT]
            if mode == TestMode.CORRECTNESS:
                args.extend(['-o', MetaArgs.OUTPUT])
        elif task == ReasoningTask.CONSISTENCY:
            args = ['consistency', '-i', MetaArgs.INPUT]
        else:
            args = ['abduction-contraction', '-i', MetaArgs.INPUT, '-r', MetaArgs.REQUEST]

        return args


class MiniMESwiftMobile(OWLReasoner):
    """MiniME Swift mobile reasoner wrapper."""

    @property
    def name(self):
        return 'Mini-ME Swift mobile'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML]

    @property
    def supported_tasks(self):
        return ReasoningTask.ALL

    @property
    def is_mobile(self):
        return True

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

        super(MiniMESwiftMobile, self).__init__(find_executable('xcodebuild'), None, None)
        self._project = project
        self._scheme = scheme
        self._classification_test = classification_test
        self._consistency_test = consistency_test
        self._abduction_contraction_test = abduction_contraction_test

    def args(self, task: str, mode: str) -> List[str]:
        return []

    def classify(self, input_file, output_file=None, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)
        task = self._run(test=self._classification_test, resource=input_file, timeout=timeout)
        return self.results_parser.parse_reasoning_stats(task)

    def consistency(self, input_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)
        task = self._run(test=self._consistency_test, resource=input_file, timeout=timeout)
        return ConsistencyResults(consistent=True, stats=self.results_parser.parse_reasoning_stats(task))

    def abduction_contraction(self, resource_file, request_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(resource_file, file_type=exc.FileType.FILE)
        exc.raise_if_not_found(request_file, file_type=exc.FileType.FILE)

        task = self._run(test=self._abduction_contraction_test,
                         resource=resource_file,
                         request=request_file,
                         timeout=timeout)

        return self.results_parser.parse_abduction_contraction_results(task)

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

        task = Task(self.path, args=args)
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
