import re
import os

from owl import OWLReasoner, OWLSyntax, Stats
from src.utils import exc, jar, proc


class HermiT(OWLReasoner):
    """HermiT reasoner wrapper."""

    # Public methods

    def __init__(self, path, owl_tool_path, vm_opts):
        """
        :param str path : Path of the HermiT jar.
        :param str owl_tool_path : Path of the owltool jar.
        :param list[str] vm_opts : Options for the Java VM.
        """
        super(HermiT, self).__init__(path)
        exc.raise_if_not_found(owl_tool_path, file_type='file')
        self.__owl_tool_path = owl_tool_path
        self.__vm_opts = vm_opts

    # Overrides

    @property
    def name(self):
        return 'HermiT'

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML, OWLSyntax.FUNCTIONAL]

    def classify(self, input_file, output_file=None, timeout=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = ['-v', '-c']
        classification_out = None

        if output_file:
            classification_out = os.path.splitext(output_file)[0] + '.owl'
            args.extend(['-P', '-o', classification_out])
        else:
            args.extend(['-o', os.devnull])

        args.append(input_file)

        call_result = jar.call(self._path,
                               args=args,
                               vm_opts=self.__vm_opts,
                               output_action=proc.OutputAction.RETURN,
                               timeout=timeout)

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
        del stdout  # Unused, for some reason HermiT returns stats via stderr.
        exc.raise_if_falsy(stdout=stderr)

        result = re.search(r'Ontology parsed in (.*) msec.', stderr)
        exc.raise_if_falsy(result=result)

        parsing_ms = float(result.group(1))

        reasoning_ms = 0.0

        for regex in [r'Reasoner created in (.*) msec.', r'...action completed in (.*) msec.']:
            result = re.search(regex, stderr)
            exc.raise_if_falsy(result=result)

            reasoning_ms += float(result.group(1))

        return Stats(parsing_ms=parsing_ms, reasoning_ms=reasoning_ms, error=stderr)
