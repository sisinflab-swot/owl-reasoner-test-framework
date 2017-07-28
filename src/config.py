import sys
from os import path

from reasoners.java import JavaReasoner
from reasoners.konclude import Konclude
from reasoners.minime import MiniME, MiniMEMobile


debug = False


class Paths(object):
    """Paths config namespace."""
    DIR = path.dirname(path.dirname(path.realpath(sys.argv[0])))
    BIN_DIR = path.join(DIR, 'bin')
    DATA_DIR = path.join(DIR, 'data')
    MOBILE_DIR = path.join(DIR, 'mobile')
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
    XCODE_PROJECT = path.join(MOBILE_DIR, 'MiniME-mobile.xcodeproj')


class Mobile(object):
    """Mobile tests config namespace."""
    SCHEME = 'MiniME-mobile'
    TEST_SCHEME = 'MiniME-mobileTests'
    CLASSIFICATION_TEST = '{}/MiniME_mobileTests/testClassification'.format(TEST_SCHEME)
    CONSISTENCY_TEST = '{}/MiniME_mobileTests/testConsistency'.format(TEST_SCHEME)
    ABDUCTION_CONTRACTION_TEST = '{}/MiniME_mobileTests/testAbductionContraction'.format(TEST_SCHEME)


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

    MINIME_MOBILE = MiniMEMobile(project=Paths.XCODE_PROJECT,
                                 scheme=Mobile.SCHEME,
                                 classification_test=Mobile.CLASSIFICATION_TEST,
                                 consistency_test=Mobile.CONSISTENCY_TEST,
                                 abduction_contraction_test=Mobile.ABDUCTION_CONTRACTION_TEST)

    MINIME_JAVA = JavaReasoner(name='MiniME Java',
                               path=Paths.MINIME_JAVA,
                               owl_tool_path=Paths.OWLTOOL,
                               vm_opts=COMMON_VM_OPTS)

    TROWL = JavaReasoner(name='TrOWL',
                         path=Paths.TROWL,
                         owl_tool_path=Paths.OWLTOOL,
                         vm_opts=COMMON_VM_OPTS)

    ALL = [FACT, HERMIT, KONCLUDE, MINIME, MINIME_MOBILE, MINIME_JAVA, TROWL]
    ALL_DESKTOP = [FACT, HERMIT, KONCLUDE, MINIME, MINIME_JAVA, TROWL]
    NON_STANDARD = [MINIME, MINIME_JAVA]

    BY_NAME = dict(zip([r.name for r in ALL], ALL))
