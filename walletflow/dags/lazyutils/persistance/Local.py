import json
import os
from abc import ABC
from os import listdir
from os.path import isfile, join, exists
import re
import pandas as pd

from walletflow.dags.lazyutils.misc.Dates import now_strftime
from walletflow.dags.lazyutils.persistance.Persistance import Persistance


class LandingLocalStorage(Persistance, ABC):

    # TODO Get from config file if has any different config than the default one
    _localstorage = '.localdata'
    _nonreadpath = 'nonread'
    _readpath = 'read'

    def __init__(self):
        super().__init__()
        self._nonreadpath = join(os.getcwd(), self._localstorage, self._nonreadpath)
        self._readpath = join(os.getcwd(), self._localstorage, self._readpath)
        if not exists(self._localstorage):
            os.mkdir(self._localstorage)

        if not exists(self._nonreadpath):
            os.mkdir(self._nonreadpath)

        if not exists(self._readpath):
            os.mkdir(self._readpath)

    def _save_dataframe(self, prefix: str, df: pd.DataFrame):
        jsonobj = json.loads(df.to_json(orient='records'))
        self._save_dict(prefix, jsonobj)

    def _save_dict(self, prefix: str, obj: dict):
        filename = join(self._nonreadpath, prefix) + '_' + now_strftime(fmt='%Y-%m-%d_%H_%M_%S') + '.json'

        with open(filename, "w") as jfile:
            json.dump(obj, jfile)

    def getallnonread(self, query: str) -> list:

        onlyfiles = [f for f in listdir(self._nonreadpath) if isfile(join(self._nonreadpath, f)) and re.match(query, f)]
        jlist = []

        for f in onlyfiles:
            with open(f) as file:
                jlist.append(json.load(file))

        return jlist
