from typing import List, Optional, Union

from src.pyutils import exc
from src.pyutils.proc import Benchmark, Jar
from .owl import MetaArgs, OWLReasoner, OWLSyntax, ReasoningTask, TestMode


class JavaReasoner(OWLReasoner):
    """OWLReasoner implementation for reasoners which use our custom Java wrapper."""

    @property
    def name(self):
        return self.__name

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML, OWLSyntax.FUNCTIONAL]

    @property
    def preferred_syntax(self):
        return OWLSyntax.FUNCTIONAL

    @property
    def supported_tasks(self):
        return [ReasoningTask.CLASSIFICATION, ReasoningTask.CONSISTENCY]

    # Public methods

    def __init__(self, name: str, path: str, owl_tool_path: Optional[str], vm_opts: List[str]):
        """
        :param name : Name of the reasoner.
        :param path : Path of the reasoner jar.
        :param owl_tool_path : Path of the owltool jar.
        :param vm_opts : Options for the Java VM.
        """
        exc.raise_if_falsy(name=name)
        if owl_tool_path:
            exc.raise_if_not_found(owl_tool_path, file_type=exc.FileType.FILE)

        super(JavaReasoner, self).__init__(path, owl_tool_path, vm_opts)
        self.__name = name

    def args(self, task: str, mode: str) -> List[str]:
        if task == ReasoningTask.CLASSIFICATION:
            args = ['classification']
            if mode == TestMode.CORRECTNESS:
                args.extend(['-o', MetaArgs.OUTPUT])
            args.append(MetaArgs.INPUT)
        elif task == ReasoningTask.CONSISTENCY:
            args = ['consistency', MetaArgs.INPUT]
        else:
            args = []

        return args

    def _run(self, args: List[str], timeout: Optional[float], mode: str) -> Union[Jar, Benchmark]:
        if mode == TestMode.MEMORY:
            jar = Jar(self.path, jar_args=args, vm_opts=['-Xms1m'] + self.vm_opts)
            result = Benchmark(jar)
        else:
            result = Jar(self.path, jar_args=args, vm_opts=self.vm_opts)

        result.run(timeout=timeout)

        return result
