import sys
from os import path

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

    KONCLUDE = path.join(BIN_DIR, 'Konclude', 'Binaries', 'Konclude')
    MINIME = path.join(BIN_DIR, 'MiniME', 'MiniME-cli')
    OWLTOOL = path.join(BIN_DIR, 'OwlTool', 'owltool.jar')

    LOG = path.join(WRK_DIR, 'log.txt')
    RESULTS = path.join(WRK_DIR, 'results.csv')


class Reasoners(object):
    """Reasoners config namespace."""
    konclude = Konclude(Paths.KONCLUDE, Paths.OWLTOOL)
    miniME = MiniME(Paths.MINIME)

    reference = konclude
    third_party = [konclude]
