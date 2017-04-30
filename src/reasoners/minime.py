import re

from reasoner import Reasoner, Stats
import src.utils.exc as exc
import src.utils.proc as proc


class MiniME(Reasoner):
    """MiniME reasoner wrapper."""

    # Overrides

    @property
    def name(self):
        return 'MiniME'

    def classify(self, input_file, output_file=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = [self._path, 'classification', '-i', input_file]

        if output_file:
            args.extend(['-o', output_file])

        call_result = proc.call(args, output_action=proc.OutputAction.RETURN)

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

        if result:
            parsing_ms = float(result.group(1))
        else:
            parsing_ms = None

        result = re.search(r'Classification: (.*) ms', stdout)

        if result:
            reasoning_ms = float(result.group(1))
        else:
            reasoning_ms = None

        return Stats(parsing_ms=parsing_ms, reasoning_ms=reasoning_ms, error=stderr)
