import os

import minime
from owl import OWLReasoner, OWLSyntax
from src.utils import exc, fileutils, jar, proc


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
        return OWLSyntax.RDFXML

    # Public methods

    def __init__(self, name, path, owl_tool_path, vm_opts):
        """
        :param str name : Name of the reasoner.
        :param str path : Path of the reasoner jar.
        :param str owl_tool_path : Path of the owltool jar.
        :param list[str] vm_opts : Options for the Java VM.
        """
        exc.raise_if_falsy(name=name)
        exc.raise_if_not_found(owl_tool_path, file_type='file')

        super(JavaReasoner, self).__init__(path)

        self.__name = name
        self.__owl_tool_path = owl_tool_path
        self.__vm_opts = vm_opts

    def classify(self, input_file, output_file=None, timeout=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = ['classification']
        classification_out = None

        if output_file:
            classification_out = os.path.splitext(output_file)[0] + '.owl'

            fileutils.remove(output_file)
            fileutils.remove(classification_out)

            args.extend(['-o', classification_out])

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

        return minime.extract_stats(call_result.stdout, call_result.stderr)

    def consistency(self, input_file, timeout=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = ['consistency', input_file]
        call_result = jar.call(self._path,
                               args=args,
                               vm_opts=self.__vm_opts,
                               output_action=proc.OutputAction.RETURN,
                               timeout=timeout)

        return minime.extract_consistency_results(call_result.stdout, call_result.stderr)

    def abduction_contraction(self, resource_file, request_file, timeout=None):
        exc.raise_if_not_found(resource_file, file_type='file')
        exc.raise_if_not_found(request_file, file_type='file')

        args = ['abduction-contraction', '-r', request_file, resource_file]
        call_result = jar.call(self._path,
                               args=args,
                               vm_opts=self.__vm_opts,
                               output_action=proc.OutputAction.RETURN,
                               timeout=timeout)

        return minime.extract_abduction_contraction_results(call_result.stdout, call_result.stderr)
