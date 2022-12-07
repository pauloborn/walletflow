from typing import List

from walletflow.dags.custom_dags.finance.normalize.cash_events import Type, CashEvent, TransactionStatus
from walletflow.dags.lazyutils.misc.Dates import conditional_strptime


def category_status_mapping(title: str, category: str) -> (str, str, Type):
    cash_flow_categories = ['payment']
    outcome_categories = ['transaction', 'rewards_canceled']
    income_categories = ['transaction_reversed', 'rewards_fee']
    cashtype = Type.IGNORE

    reversed_status_categories = ['transaction_reversed', 'rewards_canceled']
    status = TransactionStatus.CONFIRMED

    if category in outcome_categories:
        cashtype = Type.OUTCOME
    elif category in income_categories:
        cashtype = Type.INCOME
    elif category in cash_flow_categories:
        cashtype = Type.CASH_FLOW

    real_category = title  # education, studies, food, entertainment, execise etc

    if category in reversed_status_categories:
        status = TransactionStatus.REVERSED

    return real_category, status, cashtype


def card_statements_mapper(o: dict) -> CashEvent:
    category, status, expensetype = category_status_mapping(o['title'], o['category'])

    # To fix decimals (it's receiving with no decimal)
    amount = (float(o['amount']) / 100) if o['amount'] is not None else 0.0
    amount_without_taxes = (float(o['amount_without_iof']) / 100) if o['amount_without_iof'] is not None else 0.0

    transaction_channel_name = o['description']
    tm = conditional_strptime(o['time'], ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ'])

    return CashEvent(
        original_id=o['id'],
        title=transaction_channel_name,
        category=category,
        amount=amount,
        amount_without_taxes=amount_without_taxes,
        status=status,
        time=tm,
        source='Card transaction',
        type=expensetype,
        original_json=o
    )


def card_events_processor(obj: list) -> List[CashEvent]:
    return list(map(card_statements_mapper, obj))
