import unittest
import tempfile
import os

from walletflow.dags.common_package.config.Configuration import Configuration, Config
from walletflow.dags.common_package.misc.TempWritableFile import TempWritableFile


def config_template() -> str:
    return """
            [Core]
            environment = dev
            
            [Nubank]
            certification = None
            
            [LOG]
            log-level = INFO
    """


def validation_template():
    return {
        'Core': {
            'environment': 'dev'
        },
        'Nubank': {
            'certification': 'None'
        },
        'LOG': {
            'log-level': 'INFO'
        }
    }


class ConfigurationTest(unittest.TestCase):
    def test_with_config_ini(self):
        """It should look for file and load all set configurations"""

        tmp_file = TempWritableFile('configtests_')
        with tmp_file as tmp:
            tmp.write(config_template())
            tmp.flush()

            cfg: Configuration = Configuration(tmp.file_path)
            cfg_config = cfg.config
            dict_cfg = {s: dict(cfg_config.items(s)) for s in cfg_config.sections()}

            response_template = validation_template()
            self.assertDictEqual(response_template, dict_cfg, "Configuration not equal!")

    def test_static_method(self):
        """Just the same test before, but using the default configuration"""

        os.chdir(os.path.join('..', '..'))

        tmp_file = TempWritableFile('configtests_')
        with tmp_file as tmp:
            tmp.write(config_template())
            tmp.flush()

            cfg_config = Config()  # Here is the only difference
            dict_cfg = {s: dict(cfg_config.items(s)) for s in cfg_config.sections()}

            response_template = validation_template()
            self.assertDictEqual(response_template, dict_cfg, "Configuration not equal!")

        pass

    def test_check_method(self):
        """Validate if check is evaluating correctly"""
        pass


if __name__ == '__main__':
    unittest.main()
