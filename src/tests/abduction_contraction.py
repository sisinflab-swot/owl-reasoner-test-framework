import os

from src import config
from src.reasoners.owl import OWLSyntax
from src.utils.proc import WatchdogException
from test import Test


class AbductionContractionTimeTest(Test):
    """Abduction/contraction time test."""

    @property
    def name(self):
        return 'abduction/contraction time'

    def setup(self, logger, csv_writer):
        del logger  # Unused
        columns = ['Resource', 'Request']

        for reasoner in config.Reasoners.non_standard:
            columns.append('{} resource parsing'.format(reasoner.name))
            columns.append('{} request parsing'.format(reasoner.name))
            columns.append('{} reasoner init'.format(reasoner.name))
            columns.append('{} reasoning'.format(reasoner.name))

        csv_writer.writerow(columns)

    def run(self, onto_name, ontologies, logger, csv_writer):

        resource = ontologies[OWLSyntax.RDFXML].path

        dataset_dir = os.path.dirname(os.path.dirname(resource))
        requests_dir = os.path.join(dataset_dir, 'requests', os.path.splitext(onto_name)[0])

        requests = [os.path.join(requests_dir, f) for f in os.listdir(requests_dir) if f.endswith('.owl')]

        if len(requests) == 0:
            logger.log('No available requests.')
            return

        for request in requests:
            request_name = os.path.basename(request)
            logger.log('    Request: {}'.format(request_name))
            csv_row = [onto_name, request_name]

            for reasoner in config.Reasoners.non_standard:
                logger.log('        {}: '.format(reasoner.name), endl=False)
                try:
                    stats = reasoner.abduction_contraction(resource, request,
                                                           timeout=config.Reasoners.abduction_contraction_timeout)
                except WatchdogException:
                    csv_row.extend(['timeout', 'timeout', 'timeout', 'timeout'])
                    logger.log('timeout')
                except Exception:
                    csv_row.extend(['error', 'error', 'error', 'error'])
                    logger.log('error')
                else:
                    csv_row.extend([stats.resource_parsing_ms,
                                    stats.request_parsing_ms,
                                    stats.init_ms,
                                    stats.reasoning_ms])

                    logger.log(('Resource parsing {:.0f} ms | '
                                'Request parsing {:.0f} ms | '
                                'Reasoner init {:.0f} ms | '
                                'Reasoning {:.0f} ms').format(stats.resource_parsing_ms,
                                                              stats.request_parsing_ms,
                                                              stats.init_ms,
                                                              stats.reasoning_ms))
            csv_writer.writerow(csv_row)
