import sys
from os import path

from reasoners.fact import Fact
from reasoners.hermit import HermiT
from reasoners.konclude import Konclude
from reasoners.minime import MiniME


debug = True


class Paths(object):
    """Paths config namespace."""
    DIR = path.dirname(path.dirname(path.realpath(sys.argv[0])))
    BIN_DIR = path.join(DIR, 'bin')
    DATA_DIR = path.join(DIR, 'data')
    WRK_DIR = path.join(DIR, 'wrk')

    FUNC_DIR = path.join(DATA_DIR, 'functional')
    XML_DIR = path.join(DATA_DIR, 'rdfxml')
    TEMP_DIR = path.join(WRK_DIR, 'temp')

    FACT = path.join(BIN_DIR, 'Fact++', 'factcli.jar')
    HERMIT = path.join(BIN_DIR, 'HermiT', 'HermiT.jar')
    KONCLUDE = path.join(BIN_DIR, 'Konclude', 'Binaries', 'Konclude')
    MINIME = path.join(BIN_DIR, 'MiniME', 'MiniME-cli')
    OWLTOOL = path.join(BIN_DIR, 'OwlTool', 'owltool.jar')

    LOG = path.join(WRK_DIR, 'log.txt')
    RESULTS = path.join(WRK_DIR, 'results.csv')


class Reasoners(object):
    """Reasoners config namespace."""
    fact = Fact(Paths.FACT, Paths.OWLTOOL)
    hermit = HermiT(Paths.HERMIT, Paths.OWLTOOL)
    konclude = Konclude(Paths.KONCLUDE, Paths.OWLTOOL)
    miniME = MiniME(Paths.MINIME)

    reference = konclude
    all = [miniME, fact, hermit, konclude]
