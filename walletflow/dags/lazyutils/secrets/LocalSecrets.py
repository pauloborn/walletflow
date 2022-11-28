import json
from os.path import join
from walletflow.dags.lazyutils.config.Configuration import Config
from walletflow.dags.lazyutils.secrets.Secrets import Secrets


class LocalSecrets(Secrets):
    _config = None
    _folder = None
    _file = None

    def _load(self):
        self._config = Config()
        self._folder = self._config['Secrets']['folder']
        self._file = self._config['Secrets']['file']

        filepath = join(self._folder, self._file)
        with open(filepath, 'r') as f:
            self._secrets = json.load(f)
