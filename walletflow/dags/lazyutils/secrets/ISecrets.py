from enum import Enum, auto

from walletflow.dags.lazyutils.secrets.LocalSecrets import LocalSecrets


class Secrets(Enum):
    LOCAL = auto()
    AWS_SECRETS_MANAGER = auto()


def SecretsFactory(vault: Secrets):
    if vault == Secrets.LOCAL:
        local = LocalSecrets()
        local.load()
        return local
    else:
        raise NotImplementedError
