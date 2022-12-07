import json
import logging
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import Column, Sequence, Integer, String, MetaData, Table
from sqlalchemy.dialects import postgresql

from walletflow.dags.custom_dags.finance.normalize.cash_events import CashMap
from walletflow.dags.lazyutils.config.Configuration import Config
from walletflow.dags.lazyutils.persistance.IPersistance import PersistanceLayer, PersistanceFactory
from walletflow.dags.lazyutils.persistance.Rbdms import RBDMS
from walletflow.dags.lazyutils.structure.Callable import Callable


# TODO Filter, Merge and save
# TODO Filter income & outcome
# TODO User Pandas

def tags(title, tags):
    tags_by_title_map = CashMap().tags_map
    if title in tags_by_title_map:
        return list(dict.fromkeys([*tags, *tags_by_title_map[title]]))
    else:
        return list(dict.fromkeys([*tags, *["outros"]]))


def apply_tags(df):
    return tags(df['title'], df['tags'])


def apply_category(df):
    return '' if len(df['tags']) < 1 else df['tags'][0]


class Contextualize(Callable):
    config = None
    _stage = None
    _rbdms = None

    def prepare_temp_table(self, tablename: str):
        Table(
            tablename,
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('category', sa.String(), nullable=False),
            sa.Column('type', sa.String(), nullable=False),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('amount_without_taxes', sa.Float(), nullable=True),
            sa.Column('status', sa.String(), nullable=False),
            sa.Column('time', sa.DateTime(), nullable=False),
            sa.Column('source', sa.String(), nullable=True),
            sa.Column('tags', sa.ARRAY(sa.String), nullable=False),
            sa.Column('original_json', sa.JSON(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            prefixes=['TEMPORARY']
        )

        metadata = MetaData(bind=self._rbdms.connection)

        try:
            metadata.create_all(self._rbdms.engine)
        except Exception as e:
            raise e

    def run(self):
        # TODO Get all files from stage layer
        files = self._stage.getallfileslist('.')
        total = len(files)

        logging.debug(f'Contextualize going to process {total} files')

        for file in files:
            j = json.loads(self._stage.getfilecontent(file))

            df = pd.DataFrame(j)

            logging.debug(f'Loaded {len(df.index)} cash events')

            df['tags'] = df.apply(apply_tags, axis=1)
            df['category'] = df.apply(apply_category, axis=1)

            dfexpenses = df[df.type == 'expense']

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

        # TODO Save CASH FLOW events

        # TODO Remove from stage

    def __init__(self):
        self.config = Config('./config/config.ini')

        self._stage = \
            PersistanceFactory(PersistanceLayer.LOCAL, self.config['Core']['stage_layer_folder'])

        self._rbdms = RBDMS(self.config['Core']['context_path'])
