import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from pynubank import Nubank, MockHttpClient

from walletflow.dags.custom_dags.finance.commons import NuCommons
from walletflow.dags.lazyutils.misc import Dates
from walletflow.dags.lazyutils.config.Configuration import Config
from walletflow.dags.lazyutils.persistance.IPersistance import PersistanceFactory, PersistanceLayer
from walletflow.dags.lazyutils.secrets.ISecrets import SecretsFactory, Secrets


class NubankCrawler:
    last_days: int = None
    nu: Nubank = None
    config = None
    persist = None

    def get_card_events(self) -> pd.DataFrame:
        logging.debug('Starting Card Events')
        card_statements = self.nu.get_card_feed()
        df = pd.DataFrame(card_statements['events'])

        logging.debug(f'Got {df.count()} rows from card statements')
        if self.last_days:
            df = df[df['time'] > Dates.deltatime_to_strftime(self.last_days)]

        logging.info(f'Found {df.count()} rows from card statements from last {self.last_days} days')

        self.persistance.save(prefix=NuCommons.CARD_STATEMENTS, karg=df)
        return df

    def get_account_feed(self):
        has_next = True
        idx = 1
        cursor = None

        if self.last_days:
            datetime_delta_range = datetime.now() - timedelta(days=self.last_days)

        while has_next:
            feed = self.nu.get_account_feed_paginated(cursor)
            self.persistance.save(f'{NuCommons.ACCOUNT_FEED}-page_{idx}', feed)
            logging.debug(f'Got {len(feed["edges"])} nodes expenses from account')

            cursor = feed['edges'][-1]['cursor']
            has_next = feed['pageInfo']['hasNextPage']
            idx += 1

            if self.last_days and has_next:
                lastpostdate = feed['edges'][-1]['node']['postDate']
                dt = datetime.strptime(lastpostdate, '%Y-%m-%d')

                has_next = (dt > datetime_delta_range)

        logging.info(f'Got from account {idx} pages expenses from the last {self.last_days} days')

    def run(self):
        self.get_card_events()
        # self.get_account_feed() TODO Change it

    def __init__(self):
        self.config = Config(os.path.join(os.getcwd(), 'config', 'config.ini'))  # Initialize logging handler also

        self.last_days = self.config['Nubank']['since']
        if self.last_days == 'None':
            self.last_days = None
        else:
            self.last_days = int(self.last_days)

        if self.config['Core']['environment'] == 'dev':
            self.nu = Nubank(MockHttpClient())
        else:
            self.nu = Nubank()

        secrets = SecretsFactory(Secrets.LOCAL)
        self.nu.authenticate_with_cert(
            secrets.nubank['user'],
            secrets.nubank['password'],
            secrets.nubank['cert']
        )

        self.persistance = PersistanceFactory(PersistanceLayer.LOCAL, self.config['Core']['landing_layer_folder'])


if __name__ == '__main__':
    NubankCrawler().run()
