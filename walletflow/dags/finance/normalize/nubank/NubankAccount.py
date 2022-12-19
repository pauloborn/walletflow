from typing import List
from walletflow.dags.finance.common.cash_events import CashEvent, TransactionStatus, CashMap, Type
from lazyutils.misc.Dates import conditional_strptime


def source_type_map(o: dict) -> (Type, str):
    source = 'Outros'
    t = Type.IGNORE

    if o['tags'] is None:
        if o['title'] == 'Dinheiro guardado':
            t = Type.CASH_FLOW
            source = 'Investimento Nubank'

    elif 'money-out' in o['tags']:
        t = Type.OUTCOME
        if 'payments' in o['tags']:
            if 'Pagamento da fatura' == o['title']:
                source = 'Cartao Nubank'
            else:
                source = 'Boleto'
        elif o['footer'] == 'Pix':
            source = 'Pix'

    elif 'money-in' in o['tags']:
        t = Type.INCOME
        if o['footer'] == 'Pix':
            source = 'Pix'
        else:
            source = 'Transferência'

    return t, source


def account_statement_mapper(o: dict) -> CashEvent:
    obj = o['node']
    amount = amount_without_taxes = obj['amount'] if 'amount' in obj else 0.0
    status = TransactionStatus.CONFIRMED if not obj['strikethrough'] else TransactionStatus.REVERSED
    tm = conditional_strptime(obj['postDate'], ['%Y-%m-%d'])

    transaction_channel_name = obj['detail'].split('\nR$')[0]
    tags_by_title_map = CashMap().tags_map
    tags = []
    if transaction_channel_name in tags_by_title_map:
        tags = tags_by_title_map[transaction_channel_name]

    t, source = source_type_map(obj)

    return CashEvent(
        original_id=obj['id'],
        title=transaction_channel_name,
        category='' if len(tags) < 1 else tags[0],
        amount=amount,
        amount_without_taxes=amount_without_taxes,
        status=status,
        time=tm,
        source=source,
        type=t,
        original_json=o
    )


def account_statements_processor(o: dict) -> List[CashEvent]:
    return list(map(account_statement_mapper, o['edges']))
