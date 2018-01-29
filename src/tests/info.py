from src.pyutils import echo
from src.reasoners.owl import OWLSyntax
from .test import Test


class InfoTest(Test):
    """Dataset and reasoners info test."""

    @property
    def name(self):
        return 'info'

    def setup(self, logger, csv_writer):
        csv_writer.writerow(['Ontology'] + ['Size ({})'.format(s) for s in OWLSyntax.ALL])

        logger.log('Reasoners:', color=echo.Color.YELLOW)
        logger.indent_level += 1

        for reasoner in self._reasoners:
            logger.log('- {}: {}'.format(reasoner.name, ', '.join(reasoner.supported_syntaxes)))

        logger.indent_level -= 1
        logger.log('')

    def run(self, onto_name, ontologies, logger, csv_writer):
        csv_writer.writerow([onto_name] + [ontologies[s].size for s in OWLSyntax.ALL])
