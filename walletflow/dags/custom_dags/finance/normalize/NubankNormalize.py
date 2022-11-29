import logging
import json
from walletflow.dags.lazyutils.config.Configuration import Config
from walletflow.dags.lazyutils.persistance.IPersistance import PersistanceFactory, PersistanceLayer


class NubankNormalize:
    _landing = None
    _stage = None

    def run(self):
        # TODO List all files on landing page
        files = self._landing.getallfileslist()
        total = len(files)

        logging.debug(f'Normalize starting to process {total} files')

        for idx, file in enumerate(files):
            j = json.loads(self._landing.getfilecontent(file))

            # TODO Normalize account feed

            # TODO Normalize card statements

            # TODO Save file normalized to stage

            logging.debug(f'Processed {idx}/{total} files')

        logging.info('Nubank normalization finished')


    def __init__(self):
        self.config = Config()

        self._landing = PersistanceFactory(PersistanceLayer.LOCAL, self.config['Core']['landing_layer_folder'])
        self._stage = PersistanceFactory(PersistanceLayer.LOCAL, self.config['Core']['stage_layer_folder'])
