import configparser
import logging

from walletflow.dags.lazyutils.structure.Singleton import Singleton


class Configuration(Singleton):
    config = None
    _log_level: str = 'DEBUG'

    def __init__(self, config_file_path: str = './config/example-config.ini'):
        if self.config is not None:
            return

        self.config = configparser.ConfigParser()
        sections_read = self.config.read(config_file_path)

        if len(sections_read) > 0:
            self._log_level = self.config['LOG']['log-level']

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S',
            level=self._log_level
        )

        logging.getLogger().addHandler(logging.StreamHandler())

        logging.debug('== Configuration ==')
        for k in list(self.config.keys()):
            logging.debug('%s: %s', k, self.config[k])

    def check(self, keys_to_check: list) -> list:
        not_found = []
        flattened_config = [item for sublist in self.config for item in sublist]
        for k in keys_to_check:
            if k not in flattened_config:
                not_found.append(k)

        return not_found


def Config(filepath: str = ''):
    c = Configuration() if filepath == '' else Configuration(filepath)
    return c.config
