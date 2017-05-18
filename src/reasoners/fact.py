import re
import os

from owl import OWLReasoner, OWLSyntax, Stats
from src.utils import exc, jar, proc


class Fact(OWLReasoner):
    """Fact++ reasoner wrapper."""

    # Public methods

    def __init__(self, path, owl_tool_path):
        """
        :param str path : Path of the Fact++ jar.
        :param str owl_tool_path : Path of the owltool jar.
        """
        super(Fact, self).__init__(path)
        exc.raise_if_not_found(owl_tool_path, file_type='file')
        self.__owl_tool_path = owl_tool_path

    # Overrides

    @property
    def name(self):
        return 'Fact++'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML, OWLSyntax.FUNCTIONAL]

    def classify(self, input_file, output_file=None, timeout=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = ['classify']
        classification_out = None

        if output_file:
            classification_out = os.path.splitext(output_file)[0] + '.owl'
            args.extend(['-o', classification_out])

        args.append(input_file)

        lib_opt = '-Djava.library.path={}'.format(os.path.dirname(self._path))
        limit_opt = '-DentityExpansionLimit=1000000000'

        call_result = jar.call(self._path,
                               args=args,
                               vm_opts=[lib_opt, limit_opt],
                               output_action=proc.OutputAction.RETURN,
                               timeout=timeout)

        if output_file:
            args = ['print-tbox', '-o', output_file, classification_out]
            jar.call(self.__owl_tool_path, args=args, output_action=proc.OutputAction.DISCARD)

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
        result = re.search(r'Parsing: (.*) ms', stdout)

        exc.raise_if_falsy(result=result)
        parsing_ms = float(result.group(1))

        result = re.search(r'Classification: (.*) ms', stdout)
        exc.raise_if_falsy(result=result)

        reasoning_ms = float(result.group(1))

        return Stats(parsing_ms=parsing_ms, reasoning_ms=reasoning_ms, error=stderr)
