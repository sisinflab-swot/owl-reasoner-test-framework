import re
import os

from owl import OWLReasoner, OWLSyntax, Stats
from src.utils import exc, jar, proc


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

    def classify(self, input_file, output_file=None, timeout=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = [self._path, 'classification', '-i', input_file]
        classification_out = None

        if output_file:
            classification_out = os.path.splitext(output_file)[0] + '.owl'
            args.extend(['-o', classification_out])

        args.append('-v')

        call_result = proc.call(args, output_action=proc.OutputAction.RETURN, timeout=timeout)

        if output_file:
            args = ['print-tbox', '-o', output_file, classification_out]
            jar.call(self.__owl_tool_path,
                     args=args,
                     vm_opts=self.__vm_opts,
                     output_action=proc.OutputAction.DISCARD)

        return self.__extract_stats(call_result.stdout, call_result.stderr)

    # Private methods

    def __extract_stats(self, stdout, stderr):
        """Extract stats for a reasoning task by parsing stdout and stderr.

        :param str stdout : stdout.
        :param str stderr : stderr.
        :rtype : Stats
        :return : Reasoning task stats.
        """
        exc.raise_if_falsy(stdout=stdout)

        result = re.search(r'>> Ontology parsed in (.*) ms.', stdout)
        exc.raise_if_falsy(result=result)

        parsing_ms = float(result.group(1))

        reasoning_ms = 0.0

        for task in ['preprocessing', 'precomputing', 'classification']:
            result = re.search(r'>> Finished {} in (.*) ms'.format(task), stdout)
            exc.raise_if_falsy(result=result)

            reasoning_ms += float(result.group(1))

        return Stats(parsing_ms=parsing_ms, reasoning_ms=reasoning_ms, error=stderr)
