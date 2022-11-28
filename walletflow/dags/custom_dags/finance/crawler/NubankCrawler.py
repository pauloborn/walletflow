import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from pynubank import Nubank, MockHttpClient
from walletflow.dags.lazyutils.misc import Dates
from walletflow.dags.lazyutils.config.Configuration import Config
from walletflow.dags.lazyutils.persistance.IPersistance import PersistanceFactory, PersistanceLayer
from walletflow.dags.lazyutils.secrets.ISecrets import SecretsFactory, Secrets


class NubankCrawler:
    #TODO Implement to get from configuration file
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

        self.persistance.save(prefix="nubank-card-statements", karg=card_statements)
        return df

    def get_account_feed(self):
        has_next = True
        idx = 1
        cursor = None

        if self.last_days:
            datetime_delta_range = datetime.now() - timedelta(days=self.last_days)

        while has_next:
            feed = self.nu.get_account_feed_paginated(cursor)
            self.persistance.save(f'nubank-account-feed-page_{idx}', feed)
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
        self.get_account_feed()

    def __init__(self):
        self.config = Config(os.path.join(os.getcwd(), 'config', 'config.ini'))  # Initialize logging handler also

        self.last_days = self.config['Nubank']['since']
        if self.last_days == 'None':
            self.last_days = None

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

        self.persistance = PersistanceFactory(PersistanceLayer.LOCAL)


if __name__ == '__main__':
    NubankCrawler().run()

def dummy():
    # from walletflow.dags.custom_dags.finance.crawler.NubankCrawler import *
    nucrawler = NubankCrawler()
    nucrawler.last_days = 800
    nucrawler.run()
