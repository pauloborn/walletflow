import json
import logging
import os

import pandas as pd
import sqlalchemy as sa
import re
import alembic.config

from lazyutils.config.Configuration import Config
from lazyutils.persistance.IPersistance import PersistanceLayer, PersistanceFactory
from lazyutils.persistance.Rbdms import RBDMS
from lazyutils.structure.Callable import Callable

from walletflow.dags.finance.common.cash_events import CashMap


def tags(title, tags):
    if title is None:
        return []

    tags_by_title_map = CashMap().tags_map
    title_tags = tags_by_title_map[title] if title in tags_by_title_map else []

    pattern_tags_map = CashMap().pattern_tags_map
    tags_by_pattern_map = []
    title = title.lower()
    for k in pattern_tags_map:
        if bool(re.search(k, title)):
            tags_by_pattern_map = [*tags_by_pattern_map, *pattern_tags_map[k]]

    if len(tags_by_pattern_map) < 1 and len(tags) < 1 and len(title_tags) < 1:
        title_tags = ["outros"]

    return list(dict.fromkeys([*tags, *tags_by_pattern_map, *title_tags]))


def apply_tags(df):
    return tags(df['title'], df['tags'])


def apply_category(df):
    return '' if len(df['tags']) < 1 else df['tags'][0]


class Contextualize(Callable):
    config = None
    _stage = None
    _rbdms = None

    def run(self, *args, **kwargs):
        files = self._stage.getallfileslist('.')
        total = len(files)

        logging.debug(f'Contextualize going to process {total} files')

        for file in files:
            j = json.loads(self._stage.getfilecontent(file))

            df = pd.DataFrame(j)

            logging.debug(f'Loaded {len(df.index)} cash events')

            df['tags'] = df.apply(apply_tags, axis=1)
            df['category'] = df.apply(apply_category, axis=1)

            dfexpenses = df[(df.type == 'expense') & (df.source != 'Cartao Nubank')]

            with self._rbdms.engine.begin() as conn:

                dfexpenses.to_sql("#temp_expense",
                                  conn,
                                  index=False,
                                  if_exists="replace",
                                  dtype={
                                      "time": sa.types.DateTime(),
                                      "tags": sa.types.ARRAY(sa.types.String),
                                      "original_json": sa.types.JSON()
                                  }
                                  )

                conn.exec_driver_sql(
                    """
                    MERGE INTO expense AS main
                    USING (
                        SELECT original_id, title, category, amount, amount_without_taxes, status, 
                        time, source, tags, original_json, type FROM "#temp_expense"
                    ) AS temp
                    ON (main.original_id = temp.original_id)
                    WHEN matched THEN
                        UPDATE SET  
                            title = temp.title, 
                            category = temp.category, 
                            amount = temp.amount, 
                            amount_without_taxes = temp.amount_without_taxes, 
                            status = temp.status, 
                            time = temp.time, 
                            source = temp.source, 
                            tags = temp.tags, 
                            original_json = temp.original_json, 
                            type = temp.type
                    WHEN NOT matched THEN
                        INSERT (
                            original_id, 
                            title, 
                            category, 
                            amount, 
                            amount_without_taxes,
                            status, 
                            time,
                            source,
                            tags,
                            original_json,
                            type
                        ) VALUES (
                            temp.original_id, 
                            temp.title, 
                            temp.category, 
                            temp.amount, 
                            temp.amount_without_taxes,
                            temp.status, 
                            temp.time,
                            temp.source,
                            temp.tags,
                            temp.original_json,
                            temp.type)
                    """
                )

                conn.exec_driver_sql('DROP TABLE "#temp_expense"')

        self._stage.mark_as_processed_files(files)

    def __init__(self):
        base_path = os.getenv("CONFIG_PATH") if type(os.getenv("CONFIG_PATH")) is None else "/"
        self.config = Config(os.path.join(base_path, 'config', 'config.ini'))

        self._stage = \
            PersistanceFactory(PersistanceLayer.LOCAL, self.config['Core']['stage_layer_folder'])

        self._rbdms = RBDMS(self.config['Core']['context_path'])

        alembic_ini = self.config['alembic']['ini_file_path']

        alembic_args = [
            '--raiseerr',
            '-c', alembic_ini,
            'upgrade', 'head',
        ]
        alembic.config.main(argv=alembic_args)
