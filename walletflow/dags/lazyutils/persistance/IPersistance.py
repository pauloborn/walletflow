from enum import Enum, auto

from walletflow.dags.lazyutils.persistance.Local import LocalLayerStorage


class PersistanceLayer(Enum):
    LOCAL = auto()
    AWS_S3 = auto()


# TODO Implement unit tests
def PersistanceFactory(layer: PersistanceLayer = PersistanceLayer.LOCAL, path: str = ''):

    if layer is PersistanceLayer.LOCAL:
        return LocalLayerStorage(path)
    else:
        raise NotImplementedError

