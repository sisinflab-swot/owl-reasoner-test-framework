import sys
from os import path
from typing import Dict, List, Optional

from .reasoners.owl import OWLReasoner
from .reasoners.java import JavaReasoner
from .reasoners.konclude import Konclude
from .reasoners.minime import MiniMEJava2, MiniMESwift, MiniMESwiftMobile
from .reasoners.minime3 import MiniMEJava3, MiniMEObjC3


DEBUG = False


class Paths:
    """Paths config namespace."""
    DIR = path.dirname(path.dirname(path.realpath(sys.argv[0])))
    BIN_DIR = path.join(DIR, 'bin')
    DATA_DIR = path.join(DIR, 'data')
    MOBILE_DIR = path.join(DIR, 'mobile')
    RESULTS_DIR = path.join(DIR, 'results')

    FACT_DIR = path.join(BIN_DIR, 'Fact++')
    FACT = path.join(FACT_DIR, 'factcli.jar')
    HERMIT = path.join(BIN_DIR, 'HermiT', 'hermitcli.jar')
    KONCLUDE = path.join(BIN_DIR, 'Konclude', 'Binaries', 'Konclude')
    MINIME_OBJC_3 = path.join(BIN_DIR, 'MiniMEObjC3', 'MiniME-macOS-cli')
    MINIME_SWIFT = path.join(BIN_DIR, 'MiniMESwift', 'MiniME-cli')
    MINIME_JAVA_2 = path.join(BIN_DIR, 'MiniMEJava2', 'minimecli.jar')
    MINIME_JAVA_3 = path.join(BIN_DIR, 'MiniMEJava3', 'minime-java-3.0.jar')
    OWLTOOL = path.join(BIN_DIR, 'OwlTool', 'owltool.jar')
    TROWL = path.join(BIN_DIR, 'TrOWL', 'trowlcli.jar')

    XCODE_PROJECT = path.join(MOBILE_DIR, 'MiniME-mobile.xcodeproj')


class Mobile:
    """Mobile tests config namespace."""
    SCHEME = 'MiniME-mobile'
    TEST_SCHEME = 'MiniME-mobileTests'
    CLASSIFICATION_TEST = '{}/MiniME_mobileTests/testClassification'.format(TEST_SCHEME)
    CONSISTENCY_TEST = '{}/MiniME_mobileTests/testConsistency'.format(TEST_SCHEME)
    ABDUCTION_CONTRACTION_TEST = '{}/MiniME_mobileTests/testAbductionContraction'.format(TEST_SCHEME)


class Reasoners:
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

    MINIME_OBJC_3 = MiniMEObjC3(path=Paths.MINIME_OBJC_3)

    MINIME_SWIFT = MiniMESwift(path=Paths.MINIME_SWIFT)

    MINIME_SWIFT_MOBILE = MiniMESwiftMobile(project=Paths.XCODE_PROJECT,
                                            scheme=Mobile.SCHEME,
                                            classification_test=Mobile.CLASSIFICATION_TEST,
                                            consistency_test=Mobile.CONSISTENCY_TEST,
                                            abduction_contraction_test=Mobile.ABDUCTION_CONTRACTION_TEST)

    MINIME_JAVA_2 = MiniMEJava2(path=Paths.MINIME_JAVA_2,
                                owl_tool_path=Paths.OWLTOOL,
                                vm_opts=COMMON_VM_OPTS)

    MINIME_JAVA_3 = MiniMEJava3(path=Paths.MINIME_JAVA_3, vm_opts=COMMON_VM_OPTS)

    TROWL = JavaReasoner(name='TrOWL',
                         path=Paths.TROWL,
                         owl_tool_path=Paths.OWLTOOL,
                         vm_opts=COMMON_VM_OPTS)

    REFERENCE = KONCLUDE

    ALL = [FACT, HERMIT, KONCLUDE, MINIME_JAVA_2, MINIME_JAVA_3,
           MINIME_OBJC_3, MINIME_SWIFT, MINIME_SWIFT_MOBILE, TROWL]

    # Public methods

    @classmethod
    def by_name(cls, reasoners: Optional[List[OWLReasoner]] = None) -> Dict[str, OWLReasoner]:
        if not reasoners:
            reasoners = cls.ALL
        return dict(zip([r.name for r in reasoners], reasoners))

    @classmethod
    def desktop(cls, reasoners: Optional[List[OWLReasoner]] = None) -> List[OWLReasoner]:
        if not reasoners:
            reasoners = cls.ALL
        return [r for r in reasoners if not r.is_mobile]

    @classmethod
    def mobile(cls, reasoners: Optional[List[OWLReasoner]] = None) -> List[OWLReasoner]:
        if not reasoners:
            reasoners = cls.ALL
        return [r for r in reasoners if r.is_mobile]

    @classmethod
    def supporting_task(cls, task: str, reasoners: Optional[List[OWLReasoner]] = None) -> List[OWLReasoner]:
        if not reasoners:
            reasoners = cls.ALL
        return [r for r in reasoners if task in r.supported_tasks]
