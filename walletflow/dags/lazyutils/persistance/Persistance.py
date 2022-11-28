import pandas as pd


class Persistance:

    def save(self, prefix: str, karg):
        return self._save_map[type(karg)](prefix, karg)

    def _save_dict(self, prefix: str, obj: dict):
        raise NotImplementedError

    def _save_dataframe(self, prefix: str, df: pd.DataFrame):
        raise NotImplementedError

    def get(self, query: str):
        raise NotImplementedError

    def getallnonread(self, query: str):
        raise NotImplementedError

    def __init__(self):
        self._save_map = {
            pd.DataFrame: self._save_dataframe,
            dict: self._save_dict
        }
