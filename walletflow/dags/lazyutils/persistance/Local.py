import json
import os
from abc import ABC
from os import listdir
from os.path import isfile, join, exists
import re
import pandas as pd

from walletflow.dags.lazyutils.config.Configuration import Config
from walletflow.dags.lazyutils.misc.Dates import now_strftime
from walletflow.dags.lazyutils.persistance.Persistance import Persistance


class LocalLayerStorage(Persistance, ABC):

    _localstorage = '.localdata'
    _layer = 'layer'
    _processed = 'processed'

    def __init__(self, layerfolder: str):
        super().__init__()
        self.config = Config()

        if self.config.has_option('Core', 'layers_base_path'):
            self._localstorage = self.config['Core']['layers_base_path']

        if not exists(self._localstorage):
            os.mkdir(self._localstorage)

        self._layer = join(os.getcwd(), self._localstorage, layerfolder)

        if not exists(self._layer):
            os.mkdir(self._layer)

        if self.config.has_option('Core', 'layers_base_path'):
            self._processed = self.config['Core']['processed_posfix_folder']

        self._processed = join(os.getcwd(), self._localstorage, layerfolder+self._processed)

        if not exists(self._processed):
            os.mkdir(self._processed)

    def _save_dataframe(self, prefix: str, df: pd.DataFrame):
        jsonobj = json.loads(df.to_json(orient='records'))
        self._save_dict(prefix, jsonobj)

    def _save_dict(self, prefix: str, obj: dict):
        filename = join(self._layer, prefix) + '_' + now_strftime(fmt='%Y-%m-%d_%H_%M_%S') + '.json'

        with open(filename, "w") as jfile:
            json.dump(obj, jfile)

    def _save_list(self, prefix: str, obj: list):
        filename = join(self._layer, prefix) + '_' + now_strftime(fmt='%Y-%m-%d_%H_%M_%S') + '.json'

        with open(filename, "w") as f:
            json.dump(obj, f, ensure_ascii=False)

    def getallfileslist(self, query: str) -> list:
        return [f for f in listdir(self._layer) if isfile(join(self._layer, f)) and re.match(query, f)]

    def getallfiles(self, query: str) -> list:

        onlyfiles = [f for f in listdir(self._layer) if isfile(join(self._layer, f)) and re.match(query, f)]
        jlist = []

        for f in onlyfiles:
            with open(join(self._layer, f)) as file:
                jlist.append(file.read())

        return jlist

    def countallfiles(self, query: str) -> int:
        onlyfiles = [f for f in listdir(self._layer) if isfile(join(self._layer, f)) and re.match(query, f)]

        return len(onlyfiles)

    def getfilecontent(self, file: str):
        filepath = join(self._layer, file)
        with open(filepath, 'r') as f:
            return f.read()

    def mark_as_processed_files(self, files: list):
        for f in files:
            os.replace(
                join(self._layer, f),
                join(self._processed, f)
            )
