import re

from owl import AbductionContractionResults, ConsistencyResults, OWLReasoner, OWLSyntax, ReasoningStats
from src.utils import exc, fileutils, proc


class MiniME(OWLReasoner):
    """MiniME reasoner wrapper."""

    # Overrides

    @property
    def name(self):
        return 'MiniME'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML]

    @property
    def preferred_syntax(self):
        return OWLSyntax.RDFXML

    def classify(self, input_file, output_file=None, timeout=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = [self._path, 'classification', '-i', input_file]

        if output_file:
            fileutils.remove(output_file)
            args.extend(['-o', output_file])

        call_result = proc.call(args, output_action=proc.OutputAction.RETURN, timeout=timeout)

        return extract_stats(call_result.stdout)

    def consistency(self, input_file, timeout=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = [self._path, 'consistency', '-i', input_file]
        call_result = proc.call(args, output_action=proc.OutputAction.RETURN, timeout=timeout)

        return extract_consistency_results(call_result.stdout)

    def abduction_contraction(self, resource_file, request_file, timeout=None):
        exc.raise_if_not_found(resource_file, file_type='file')
        exc.raise_if_not_found(request_file, file_type='file')

        args = [self._path, 'abduction-contraction', '-i', resource_file, '-r', request_file]
        call_result = proc.call(args, output_action=proc.OutputAction.RETURN, timeout=timeout)

        return extract_abduction_contraction_results(call_result.stdout)


# Utility functions


def extract_stats(stdout):
    """Extract stats for a reasoning task by parsing stdout.

    :param str stdout : stdout.
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

    return ReasoningStats(parsing_ms=parsing_ms, reasoning_ms=reasoning_ms)


def extract_consistency_results(stdout):
    """Extract the result of the consistency task by parsing stdout.

    :param str stdout : stdout.
    :rtype : ConsistencyResults
    :return : Consistency task results.
    """
    stats = extract_stats(stdout)

    result = re.search(r'The ontology is (.*)\.', stdout)
    exc.raise_if_falsy(result=result)
    consistent = (result.group(1) == 'consistent')

    return ConsistencyResults(consistent, stats)


def extract_abduction_contraction_results(stdout):
    """Extract the result of the consistency task by parsing stdout.

    :param str stdout : stdout.
    :rtype : AbductionContractionResults
    :return : Abduction/contraction task results.
    """
    exc.raise_if_falsy(stdout=stdout)

    result = re.search(r'Resource parsing: (.*) ms', stdout)
    exc.raise_if_falsy(result=result)
    res_parsing_ms = float(result.group(1))

    result = re.search(r'Request parsing: (.*) ms', stdout)
    exc.raise_if_falsy(result=result)
    req_parsing_ms = float(result.group(1))

    result = re.search(r'Reasoner initialization: (.*) ms', stdout)
    exc.raise_if_falsy(result=result)
    init_ms = float(result.group(1))

    result = re.search(r'Reasoning: (.*) ms', stdout)
    exc.raise_if_falsy(result=result)
    reasoning_ms = float(result.group(1))

    return AbductionContractionResults(resource_parsing_ms=res_parsing_ms,
                                       request_parsing_ms=req_parsing_ms,
                                       init_ms=init_ms,
                                       reasoning_ms=reasoning_ms)
