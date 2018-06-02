from typing import List, Optional

from src.pyutils import exc
from .owl import MetaArgs, OWLReasoner, ReasoningTask, TestMode


class JavaReasoner(OWLReasoner):
    """OWLReasoner implementation for reasoners which use our custom Java wrapper."""

    @property
    def name(self):
        return self.__name

    def __init__(self, name: str, path: str, owl_tool_path: Optional[str], vm_opts: List[str]):
        """
        :param name : Name of the reasoner.
        :param path : Path of the reasoner jar.
        :param owl_tool_path : Path of the owltool jar.
        :param vm_opts : Options for the Java VM.
        """
        exc.raise_if_falsy(name=name)
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
