import re

from owl import ConsistencyResults, OWLReasoner, OWLSyntax, ReasoningStats
from src.utils import exc, proc


class MiniME(OWLReasoner):
    """MiniME reasoner wrapper."""

    # Overrides

    @property
    def name(self):
        return 'MiniME'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML]

    def classify(self, input_file, output_file=None, timeout=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = [self._path, 'classification', '-i', input_file]

        if output_file:
            args.extend(['-o', output_file])

        call_result = proc.call(args, output_action=proc.OutputAction.RETURN, timeout=timeout)

        return extract_stats(call_result.stdout, call_result.stderr)

    def consistency(self, input_file, timeout=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = [self._path, 'consistency', '-i', input_file]
        call_result = proc.call(args, output_action=proc.OutputAction.RETURN, timeout=timeout)

        return extract_consistency_results(call_result.stdout, call_result.stderr)


# Utility functions


def extract_stats(stdout, stderr):
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

    result = re.search(r'Reasoning: (.*) ms', stdout)
    exc.raise_if_falsy(result=result)
    reasoning_ms = float(result.group(1))

    return ReasoningStats(parsing_ms=parsing_ms, reasoning_ms=reasoning_ms, error=stderr)


def extract_consistency_results(stdout, stderr):
    """Extract the result of the consistency task by parsing stdout and stderr.

    :param str stdout : stdout.
    :param str stderr : stderr.
    :rtype : ConsistencyResults
    :return : Consistency task results.
    """
    stats = extract_stats(stdout, stderr)

    result = re.search(r'The ontology is (.*)\.', stdout)
    exc.raise_if_falsy(result=result)
    consistent = (result.group(1) == 'consistent')

    return ConsistencyResults(consistent, stats)
