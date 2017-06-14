import re
import os

from owl import ConsistencyResults, OWLReasoner, OWLSyntax, ReasoningStats
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

    @property
    def preferred_syntax(self):
        return OWLSyntax.FUNCTIONAL

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

        return self.__extract_classification_stats(call_result.stdout, call_result.stderr)

    def consistency(self, input_file, timeout=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = [self._path, 'consistency', '-i', input_file, '-v']
        call_result = proc.call(args, output_action=proc.OutputAction.RETURN, timeout=timeout)

        return self.__extract_consistency_results(call_result.stdout, call_result.stderr)

    def abduction_contraction(self, resource_file, request_file, timeout=None):
        raise NotImplementedError

    # Private methods

    def __extract_stats(self, stdout, stderr):
        """Extract stats for a reasoning task by parsing stdout and stderr.

        :param str stdout : stdout.
        :param str stderr : stderr.
        :rtype : Stats
        :return : Reasoning task stats.
        """
        exc.raise_if_falsy(stdout=stdout)

        result = re.search(r'>> Ontology parsed in (.*) ms\.', stdout)
        exc.raise_if_falsy(result=result)
        parsing_ms = float(result.group(1))

        result = re.search(r'Total processing time: (.*) ms\.', stdout)
        exc.raise_if_falsy(result=result)
        total_ms = float(result.group(1))

        return ReasoningStats(parsing_ms=parsing_ms, reasoning_ms=(total_ms - parsing_ms), error=stderr)

    def __extract_classification_stats(self, stdout, stderr):
        """Extract stats for the classification task by parsing stdout and stderr.

        :param str stdout : stdout.
        :param str stderr : stderr.
        :rtype : Stats
        :return : Reasoning task stats.
        """
        stats = self.__extract_stats(stdout, stderr)

        result = re.search(r'Query \'UnnamedWriteClassHierarchyQuery\' processed in \'(.*)\' ms\.', stdout)

        if result:
            write_ms = float(result.group(1))
            stats.reasoning_ms -= write_ms

        return stats

    def __extract_consistency_results(self, stdout, stderr):
        """Extract the result of the consistency task by parsing stdout and stderr.

        :param str stdout : stdout.
        :param str stderr : stderr.
        :rtype : ConsistencyResults
        :return : Consistency task results.
        """
        stats = self.__extract_stats(stdout, stderr)

        result = re.search(r'Ontology \'.*\' is (.*)\.', stdout)
        exc.raise_if_falsy(result=result)
        consistent = (result.group(1) == 'consistent')

        return ConsistencyResults(consistent, stats)
