import os
from typing import List, Optional, Union

from src.pyutils import exc, fileutils
from src.pyutils.proc import Benchmark, Jar, OutputAction
from . import minime
from .owl import OWLReasoner, OWLSyntax, TestMode


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

    # Public methods

    def __init__(self, name: str, path: str, owl_tool_path: str, vm_opts: List[str]):
        """
        :param name : Name of the reasoner.
        :param path : Path of the reasoner jar.
        :param owl_tool_path : Path of the owltool jar.
        :param vm_opts : Options for the Java VM.
        """
        exc.raise_if_falsy(name=name)
        exc.raise_if_not_found(owl_tool_path, file_type=exc.FileType.FILE)

        super(JavaReasoner, self).__init__(path)

        self.__name = name
        self.__owl_tool_path = owl_tool_path
        self.__vm_opts = vm_opts

    def classify(self, input_file, output_file=None, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)

        args = ['classification']
        classification_out = None

        if mode == TestMode.CORRECTNESS:
            classification_out = os.path.splitext(output_file)[0] + '.owl'

            fileutils.remove(output_file)
            fileutils.remove(classification_out)

            args.extend(['-o', classification_out])

        args.append(input_file)
        result = self._run(args, timeout=timeout, mode=mode)

        if mode == TestMode.CORRECTNESS:
            args = ['print-tbox', '-o', output_file, classification_out]
            jar = Jar(self.__owl_tool_path, jar_args=args, vm_opts=self.__vm_opts, output_action=OutputAction.DISCARD)
            jar.run()

        return minime.extract_stats(result)

    def consistency(self, input_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(input_file, file_type=exc.FileType.FILE)
        result = self._run(['consistency', input_file], timeout=timeout, mode=mode)
        return minime.extract_consistency_results(result)

    def abduction_contraction(self, resource_file, request_file, timeout=None, mode=TestMode.CORRECTNESS):
        exc.raise_if_not_found(resource_file, file_type=exc.FileType.FILE)
        exc.raise_if_not_found(request_file, file_type=exc.FileType.FILE)

        args = ['abduction-contraction', '-r', request_file, resource_file]
        result = self._run(args, timeout=timeout, mode=mode)

        return minime.extract_abduction_contraction_results(result)

    # Private methods

    def _run(self, args: List[str], timeout: Optional[float], mode: str) -> Union[Jar, Benchmark]:
        if mode == TestMode.MEMORY:
            jar = Jar(self._path, jar_args=args, vm_opts=['-Xms1m'] + self.__vm_opts)
            result = Benchmark(jar)
        else:
            result = Jar(self._path, jar_args=args, vm_opts=self.__vm_opts)

        result.run(timeout=timeout)

        return result
