import sys
from os import path

from reasoners.java import JavaReasoner
from reasoners.konclude import Konclude
from reasoners.minime import MiniME


debug = False


class Paths(object):
    """Paths config namespace."""
    DIR = path.dirname(path.dirname(path.realpath(sys.argv[0])))
    BIN_DIR = path.join(DIR, 'bin')
    DATA_DIR = path.join(DIR, 'data')
    WRK_DIR = path.join(DIR, 'wrk')
    TEMP_DIR = path.join(WRK_DIR, 'temp')

    FACT_DIR = path.join(BIN_DIR, 'Fact++')
    FACT = path.join(FACT_DIR, 'factcli.jar')
    HERMIT = path.join(BIN_DIR, 'HermiT', 'hermitcli.jar')
    KONCLUDE = path.join(BIN_DIR, 'Konclude', 'Binaries', 'Konclude')
    MINIME = path.join(BIN_DIR, 'MiniME', 'MiniME-cli')
    MINIME_JAVA = path.join(BIN_DIR, 'MiniMEJava', 'minimecli.jar')
    OWLTOOL = path.join(BIN_DIR, 'OwlTool', 'owltool.jar')
    TROWL = path.join(BIN_DIR, 'TrOWL', 'trowlcli.jar')

    LOG = path.join(WRK_DIR, 'log.txt')
    RESULTS = path.join(WRK_DIR, 'results.csv')


class Reasoners(object):
    """Reasoners config namespace."""
    classification_timeout = 300.0
    consistency_timeout = 120.0
    abduction_contraction_timeout = 60.0

    common_vm_opts = ['-Xmx16g', '-DentityExpansionLimit=1000000000']

    fact = JavaReasoner(name='Fact++',
                        path=Paths.FACT,
                        owl_tool_path=Paths.OWLTOOL,
                        vm_opts=common_vm_opts + ['-Djava.library.path={}'.format(Paths.FACT_DIR)])

    hermit = JavaReasoner(name='HermiT',
                          path=Paths.HERMIT,
                          owl_tool_path=Paths.OWLTOOL,
                          vm_opts=common_vm_opts)

    konclude = Konclude(path=Paths.KONCLUDE,
                        owl_tool_path=Paths.OWLTOOL,
                        vm_opts=common_vm_opts)

    miniME = MiniME(path=Paths.MINIME)

    miniMEJava = JavaReasoner(name='MiniME Java',
                              path=Paths.MINIME_JAVA,
                              owl_tool_path=Paths.OWLTOOL,
                              vm_opts=common_vm_opts)

    trowl = JavaReasoner(name='TrOWL',
                         path=Paths.TROWL,
                         owl_tool_path=Paths.OWLTOOL,
                         vm_opts=common_vm_opts)

    reference = konclude
    all = [fact, hermit, konclude, miniME, miniMEJava, trowl]
    non_standard = [miniME, miniMEJava]

    by_name = dict(zip([r.name for r in all], all))
