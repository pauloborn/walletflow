import logging
from datetime import datetime, timedelta


# TODO Implement unit tests
from typing import List


def deltatime_to_strftime(delta: int, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    dt = datetime.now() - timedelta(days=delta)
    return dt.strftime(fmt)


def now_strftime(fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    return datetime.now().strftime(fmt)


def conditional_strptime(tm: str, formats: List[str], ignoreerrors: bool = True) -> datetime:

    for fm in formats:
        try:
            return datetime.strptime(tm, fm)
        except ValueError:
            logging.debug(f'Format {fm} not valid for string {tm}')

    if ignoreerrors:
        return datetime.now()
    else:
        raise Exception('Not possible to format datetime string')