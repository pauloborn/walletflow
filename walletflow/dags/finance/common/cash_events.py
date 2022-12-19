import json
import re

from os.path import join
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import List

from lazyutils.structure.Singleton import Singleton


class Type(Enum):
    OUTCOME = 'expense'
    INCOME = 'income'
    CASH_FLOW = 'cash_flow'
    IGNORE = 'ignore'


class TransactionStatus(Enum):
    CONFIRMED = 'confirmed'
    REVERSED = 'reversed'


@dataclass(frozen=True)
class CashEvent:
    """Class to controle expense item"""
    original_id: str  # Original ID from bank provider
    title: str  # Expense title, i.e., 'Amazon.Com.Br Digital'
    category: str  # Category, i.e., 'educa\u00e7\u00e3o'
    amount: float  # Expense value
    amount_without_taxes: float  # Amount without taxes
    status: TransactionStatus  # Some expenses can be reverted or cancelled, this indicates if was the case
    time: datetime  # Transaction time 2022-11-27T13:04:01Z
    source: str  # Expense origin (Pix, Card transaction, transfer etc)
    original_json: dict  # Original json to help maintanence

    type: Type = Type.OUTCOME
    tags: List[str] = field(default_factory=list)  # Tags that identify by group this expense/outcome

    def to_json(self):
        return {
            'original_id': self.original_id,
            'title': self.title,
            'category': self.category,
            'amount': self.amount,
            'amount_without_taxes': self.amount_without_taxes,
            'status': self.status.value,
            'time': self.time.strftime('%Y-%m-%d %H:%M:%S'),
            'source': self.source,
            'tags': self.tags,
            'type': self.type.value,
            'original_json': self.original_json
        }


class CashMap(Singleton):
    _tags_map = None
    _pattern_tags_map = None

    @property
    def tags_map(self):
        if self._tags_map is not None:
            return self._tags_map

        filepath = join(Path(__file__).resolve().parent, "tags_map.json")

        with open(filepath) as f:
            j = f.read()
            self._tags_map = json.loads(j)

        return self._tags_map

    @property
    def pattern_tags_map(self):
        if self._pattern_tags_map is not None:
            return self._pattern_tags_map

        filepath = join(Path(__file__).resolve().parent, "tags_pattern.json")

        with open(filepath) as f:
            j = json.loads(f.read())
            self._pattern_tags_map = {}

            for k in j:
                new_key = ".*?" + re.sub("[^a-zA-Z0-9 \n\.]", ".?", k.lower()) + ".*?"
                self._pattern_tags_map[new_key] = j[k]

        return self._pattern_tags_map
