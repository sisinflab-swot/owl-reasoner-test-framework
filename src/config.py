import sys
from os import path

from reasoners.minime import MiniME
from reasoners.konclude import Konclude


debug = True


class Paths(object):
    """Paths config namespace."""
    DIR = path.dirname(path.dirname(path.realpath(sys.argv[0])))
    BIN_DIR = path.join(DIR, 'bin')
    RES_DIR = path.join(DIR, 'res')
    WRK_DIR = path.join(DIR, 'wrk')

    FUNC_DIR = path.join(RES_DIR, 'dataset', 'functional')
    XML_DIR = path.join(RES_DIR, 'dataset', 'rdfxml')
    TEMP_DIR = path.join(WRK_DIR, 'temp')

    KONCLUDE = path.join(BIN_DIR, 'Konclude', 'Binaries', 'Konclude')
    MINIME = path.join(BIN_DIR, 'MiniME', 'MiniME-cli')
    OWLTOOL = path.join(BIN_DIR, 'OwlTool', 'owltool.jar')

    LOG = path.join(WRK_DIR, 'log.txt')


class Reasoners(object):
    """Reasoners config namespace."""
    konclude = Konclude(Paths.KONCLUDE, Paths.OWLTOOL)
    miniME = MiniME(Paths.MINIME)

    all = [konclude, miniME]
