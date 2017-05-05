import re
import os

from owl import OWLReasoner, OWLSyntax, Stats
from src.utils import exc, jar, proc


class Konclude(OWLReasoner):
    """Konclude reasoner wrapper."""

    # Public methods

    def __init__(self, path, owl_tool_path):
        """
        :param str path : Path of the Konclude executable.
        :param str owl_tool_path : Path of the owltool jar.
        """
        super(Konclude, self).__init__(path)
        exc.raise_if_not_found(owl_tool_path, file_type='file')
        self.__owl_tool_path = owl_tool_path

    # Overrides

    @property
    def name(self):
        return 'Konclude'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.FUNCTIONAL]

    def classify(self, input_file, output_file=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = [self._path, 'classification', '-i', input_file]
        classification_out = None

        if output_file:
            classification_out = os.path.splitext(output_file)[0] + '.owl'
            args.extend(['-o', classification_out])

        args.append('-v')

        call_result = proc.call(args, output_action=proc.OutputAction.RETURN)

        if output_file:
            args = ['print-tbox', '-o', output_file, classification_out]
            jar.call(self.__owl_tool_path, args=args, output_action=proc.OutputAction.RETURN)

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

        reasoning_ms = None

        for task in ['preprocessing', 'precomputing', 'classification']:
            result = re.search(r'>> Finished {} in (.*) ms'.format(task), stdout)

            if result:
                ms = float(result.group(1))
                if reasoning_ms is None:
                    reasoning_ms = ms
                else:
                    reasoning_ms += ms

        exc.raise_if_none(reasoning_ms=reasoning_ms)

        return Stats(parsing_ms=parsing_ms, reasoning_ms=reasoning_ms, error=stderr)
