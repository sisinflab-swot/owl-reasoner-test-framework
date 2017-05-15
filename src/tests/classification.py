import filecmp
import os

from src import config
from src.reasoners.owl import OWLSyntax
from src.utils import echo, fileutils
from test import Test


class ClassificationCorrectnessTest(Test):
    """Classification correctness test."""

    @property
    def name(self):
        return 'classification correctness'

    def __init__(self):
        self.reference_out = os.path.join(config.Paths.TEMP_DIR, 'reference.txt')
        self.minime_out = os.path.join(config.Paths.TEMP_DIR, 'minime.txt')

    def setup(self, logger, csv_writer):
        del logger  # Unused
        csv_writer.writerow(['Ontology', 'Result', 'Failure reason'])

    def run(self, onto_name, ontologies, logger, csv_writer):

        fileutils.remove_dir_contents(config.Paths.TEMP_DIR)

        reference = config.Reasoners.reference
        minime = config.Reasoners.miniME

        func_ontology = next(onto for onto in ontologies if onto.syntax == OWLSyntax.FUNCTIONAL)
        xml_ontology = next(onto for onto in ontologies if onto.syntax == OWLSyntax.RDFXML)

        # Classify
        logger.log('{}: '.format(minime.name), endl=False)
        minime_stats = minime.classify(xml_ontology.path, output_file=self.minime_out)
        logger.log('Parsing {:.0f} ms | Classification {:.0f} ms'.format(minime_stats.parsing_ms,
                                                                         minime_stats.reasoning_ms))

        logger.log('{}: '.format(reference.name), endl=False)
        ref_stats = reference.classify(func_ontology.path, output_file=self.reference_out)
        logger.log('Parsing {:.0f} ms | Classification {:.0f} ms'.format(ref_stats.parsing_ms,
                                                                         ref_stats.reasoning_ms))

        # Results
        logger.log('Result: ', endl=False)

        if filecmp.cmp(self.reference_out, self.minime_out, shallow=False):
            logger.log('success', color=echo.Color.GREEN)
            csv_writer.writerow([onto_name, 'success'])
        else:
            logger.log('failure', color=echo.Color.RED)

            # Attempt to detect failure reason
            logger.log('Reason: ', endl=False)

            if 'raptor error -' in minime_stats.error:
                reason = 'raptor parsing error'
            elif fileutils.contains(xml_ontology.path, '// General axioms'):
                reason = 'contains general concept inclusions'
            else:
                reason = 'unknown'

            logger.log(reason, color=echo.Color.YELLOW)
            csv_writer.writerow([onto_name, 'failure', reason])


class ClassificationTimeTest(Test):
    """Classification turnaround time test."""

    @property
    def name(self):
        return 'classification time'

    def setup(self, logger, csv_writer):
        del logger  # Unused

        columns = ['Ontology']

        for reasoner in config.Reasoners.all:
            for syntax in reasoner.supported_syntaxes:
                columns.append('{} {} parsing'.format(reasoner.name, syntax))
                columns.append('{} {} classification'.format(reasoner.name, syntax))

        csv_writer.writerow(columns)

    def run(self, onto_name, ontologies, logger, csv_writer):

        results = []

        for reasoner in config.Reasoners.all:
            logger.log('- {}:'.format(reasoner.name))

            for ontology in ontologies:
                if ontology.syntax not in reasoner.supported_syntaxes:
                    continue

                stats = reasoner.classify(ontology.path)
                results.extend([stats.parsing_ms, stats.reasoning_ms])
                logger.log('    {}: Parsing {:.0f} ms | Classification {:.0f} ms'.format(ontology.syntax,
                                                                                         stats.parsing_ms,
                                                                                         stats.reasoning_ms))
        csv_writer.writerow([onto_name] + results)
