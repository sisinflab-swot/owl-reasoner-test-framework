import re

from reasoner import Reasoner, Stats
from src.utils import exc, proc


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

        exc.raise_if_falsy(result=result)
        parsing_ms = float(result.group(1))

        result = re.search(r'Classification: (.*) ms', stdout)
        exc.raise_if_falsy(result=result)

        reasoning_ms = float(result.group(1))

        return Stats(parsing_ms=parsing_ms, reasoning_ms=reasoning_ms, error=stderr)
