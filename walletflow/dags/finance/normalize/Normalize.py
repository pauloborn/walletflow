import logging
import json
import os
from typing import List

from lazyutils.structure.Callable import Callable
from lazyutils.config.Configuration import Config
from lazyutils.persistance.IPersistance import PersistanceFactory, PersistanceLayer

from walletflow.dags.finance.common.cash_events import CashEvent
from walletflow.dags.finance.normalize.nubank.NubankAccount import account_statements_processor
from walletflow.dags.finance.normalize.nubank.NubankCard import card_events_processor


class Normalize(Callable):
    _landing = None
    _stage = None

    def run(self, *args, **kwargs):
        files = self._landing.getallfileslist('.')
        total = len(files)
        cash_events: List[CashEvent] = list()

        logging.debug(f'Normalize starting to process {total} files')

        for idx, file in enumerate(files):
            j = json.loads(self._landing.getfilecontent(file))
            filename = str(file)

            if filename.startswith('nubank-card-statements'):
                evts_lst = card_events_processor(j)
                cash_events = [*cash_events, *evts_lst]
            elif filename.startswith('nubank-account'):
                statements = account_statements_processor(j)
                cash_events = [*cash_events, *statements]

            logging.debug(f'Processed {idx}/{total} files')

        self._stage.save(prefix='normalized', karg=[item.to_json() for item in cash_events])

        self._landing.mark_as_processed_files(files)

        logging.info(f'Nubank normalization finished with {len(cash_events)} cash events processed')
        logging.debug([str(evt) for evt in cash_events])

    def __init__(self):
        base_path = os.getenv("CONFIG_PATH") if type(os.getenv("CONFIG_PATH")) is None else "/"
        self.config = Config(os.path.join(base_path, 'config', 'config.ini'))

        self._landing = \
            PersistanceFactory(PersistanceLayer.LOCAL, self.config['Core']['landing_layer_folder'])

        self._stage = \
            PersistanceFactory(PersistanceLayer.LOCAL, self.config['Core']['stage_layer_folder'])
