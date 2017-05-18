import os
import re
from abc import ABCMeta, abstractmethod, abstractproperty

from src.utils import exc, fileutils, jar, proc


class OWLReasoner(object):
    """Abstract reasoner interface."""
    __metaclass__ = ABCMeta

    # Public properties

    @abstractproperty
    def name(self):
        """:rtype : str"""
        pass

    @abstractproperty
    def supported_syntaxes(self):
        """:rtype : list[str]"""
        pass

    # Public methods

    def __init__(self, path):
        """:param str path : Path of the reasoner executable."""
        exc.raise_if_not_found(path, file_type='file')
        self._path = path

    @abstractmethod
    def classify(self, input_file, output_file=None, timeout=None):
        """Performs the classification reasoning task.

        :param str input_file : Path of the input ontology.
        :param str output_file : Path of the output file.
        :param float timeout : Timeout (s).
        :rtype : Stats
        :return : Stats for the classification task.
        """
        pass


class OWLReasonerJavaWrapper(OWLReasoner):
    """OWLReasoner implementation for reasoners which use the Java wrapper."""

    @property
    def name(self):
        return self.__name

    @property
    def supported_syntaxes(self):
        return [OWLSyntax.RDFXML, OWLSyntax.FUNCTIONAL]

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

        super(OWLReasonerJavaWrapper, self).__init__(path)

        self.__name = name
        self.__owl_tool_path = owl_tool_path
        self.__vm_opts = vm_opts

    def classify(self, input_file, output_file=None, timeout=None):
        exc.raise_if_not_found(input_file, file_type='file')

        args = ['classify']
        classification_out = None

        if output_file:
            classification_out = os.path.splitext(output_file)[0] + '.owl'
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


class OWLOntology(object):
    """Models ontology files."""

    @property
    def name(self):
        """:rtype : str"""
        return os.path.basename(self.path)

    @property
    def readable_size(self):
        """:rtype : str"""
        return fileutils.human_readable_size(self.path)

    def __init__(self, path, syntax):
        """
        :param str path : The path of the ontology.
        :param str syntax : The syntax of the ontology.
        """
        exc.raise_if_not_found(path, file_type='file')
        self.path = path
        self.syntax = syntax


class OWLSyntax(object):
    """OWL ontology syntax namespace."""
    RDFXML = 'rdfxml'
    FUNCTIONAL = 'functional'


class Stats(object):
    """Contains stats about a reasoning task."""

    def __init__(self, parsing_ms=0.0, reasoning_ms=0.0, error=None):
        """
        :param float parsing_ms : Parsing time in ms.
        :param float reasoning_ms : Reasoning time in ms.
        :param str error : Error message.
        """
        self.parsing_ms = parsing_ms
        self.reasoning_ms = reasoning_ms
        self.error = error
