from enum import Enum, auto

from walletflow.dags.lazyutils.persistance.Local import LandingLocalStorage


class PersistanceLayer(Enum):
    LOCAL = auto()
    AWS_S3 = auto()

# TODO Implement unit tests
def PersistanceFactory(layer: PersistanceLayer = PersistanceLayer.LOCAL):

    if layer is PersistanceLayer.LOCAL:
        return LandingLocalStorage()
    else:
        raise NotImplementedError

