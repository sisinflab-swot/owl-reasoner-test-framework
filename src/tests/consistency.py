from src import config
from src.reasoners.owl import OWLSyntax
from src.utils import echo
from src.utils.proc import WatchdogException
from test import Test


class ConsistencyCorrectnessTest(Test):
    """Consistency correctness test."""

    @property
    def name(self):
        return 'consistency correctness'

    def setup(self, logger, csv_writer):
        del logger  # Unused
        csv_writer.writerow(['Ontology', config.Reasoners.miniME.name, config.Reasoners.reference.name, 'Result'])

    def run(self, onto_name, ontologies, logger, csv_writer):

        reference = config.Reasoners.reference
        minime = config.Reasoners.miniME

        func_ontology = next(onto for onto in ontologies if onto.syntax == OWLSyntax.FUNCTIONAL)
        xml_ontology = next(onto for onto in ontologies if onto.syntax == OWLSyntax.RDFXML)

        # Check consistency
        logger.log('{}: '.format(minime.name), endl=False)
        minime_results = minime.consistency(xml_ontology.path)
        logger.log('Parsing {:.0f} ms | Consistency {:.0f} ms'.format(minime_results.stats.parsing_ms,
                                                                      minime_results.stats.reasoning_ms))

        logger.log('{}: '.format(reference.name), endl=False)
        ref_results = reference.consistency(func_ontology.path)
        logger.log('Parsing {:.0f} ms | Consistency {:.0f} ms'.format(ref_results.stats.parsing_ms,
                                                                      ref_results.stats.reasoning_ms))

        # Results
        minime_consistent = 'consistent' if minime_results.consistent else 'inconsistent'
        ref_consistent = 'consistent' if ref_results.consistent else 'inconsistent'

        logger.log('Result: {} | '.format(minime_consistent), endl=False)
        csv_row = [onto_name, minime_consistent, ref_consistent]

        if minime_results.consistent == ref_results.consistent:
            logger.log('success', color=echo.Color.GREEN)
            csv_row.append('success')
        else:
            logger.log('failure', color=echo.Color.RED)
            csv_row.append('failure')

        csv_writer.writerow(csv_row)


class ConsistencyTimeTest(Test):
    """Consistency turnaround time test."""

    @property
    def name(self):
        return 'consistency time'

    def setup(self, logger, csv_writer):
        del logger  # Unused

        columns = ['Ontology']

        for reasoner in config.Reasoners.all:
            for syntax in reasoner.supported_syntaxes:
                columns.append('{} {} parsing'.format(reasoner.name, syntax))
                columns.append('{} {} consistency'.format(reasoner.name, syntax))

        csv_writer.writerow(columns)

    # noinspection PyBroadException
    def run(self, onto_name, ontologies, logger, csv_writer):

        csv_row = [onto_name]

        for reasoner in config.Reasoners.all:
            logger.log('- {}:'.format(reasoner.name))

            for ontology in ontologies:
                if ontology.syntax not in reasoner.supported_syntaxes:
                    continue

                try:
                    results = reasoner.consistency(ontology.path, timeout=config.Reasoners.classification_timeout)
                except WatchdogException:
                    csv_row.extend(['timeout', 'timeout'])
                    logger.log('    {}: timeout'.format(ontology.syntax))
                except Exception:
                    csv_row.extend(['error', 'error'])
                    logger.log('    {}: error'.format(ontology.syntax))
                else:
                    stats = results.stats
                    csv_row.extend([stats.parsing_ms, stats.reasoning_ms])
                    logger.log('    {}: Parsing {:.0f} ms | Classification {:.0f} ms'.format(ontology.syntax,
                                                                                             stats.parsing_ms,
                                                                                             stats.reasoning_ms))

        csv_writer.writerow(csv_row)
