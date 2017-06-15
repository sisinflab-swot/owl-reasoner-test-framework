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
    CLASSIFICATION_TIMEOUT = 1200.0
    CONSISTENCY_TIMEOUT = 1200.0
    ABDUCTION_CONTRACTION_TIMEOUT = 1200.0

    CLASSIFICATION_ITERATIONS = 5
    CONSISTENCY_ITERATIONS = 5
    ABDUCTION_CONTRACTION_ITERATIONS = 5

    COMMON_VM_OPTS = ['-Xmx16g', '-DentityExpansionLimit=1000000000']

    FACT = JavaReasoner(name='Fact++',
                        path=Paths.FACT,
                        owl_tool_path=Paths.OWLTOOL,
                        vm_opts=COMMON_VM_OPTS + ['-Djava.library.path={}'.format(Paths.FACT_DIR)])

    HERMIT = JavaReasoner(name='HermiT',
                          path=Paths.HERMIT,
                          owl_tool_path=Paths.OWLTOOL,
                          vm_opts=COMMON_VM_OPTS)

    KONCLUDE = Konclude(path=Paths.KONCLUDE,
                        owl_tool_path=Paths.OWLTOOL,
                        vm_opts=COMMON_VM_OPTS)

    MINIME = MiniME(path=Paths.MINIME)

    MINIMEJAVA = JavaReasoner(name='MiniME Java',
                              path=Paths.MINIME_JAVA,
                              owl_tool_path=Paths.OWLTOOL,
                              vm_opts=COMMON_VM_OPTS)

    TROWL = JavaReasoner(name='TrOWL',
                         path=Paths.TROWL,
                         owl_tool_path=Paths.OWLTOOL,
                         vm_opts=COMMON_VM_OPTS)

    ALL = [FACT, HERMIT, KONCLUDE, MINIME, MINIMEJAVA, TROWL]
    NON_STANDARD = [MINIME, MINIMEJAVA]

    BY_NAME = dict(zip([r.name for r in ALL], ALL))
