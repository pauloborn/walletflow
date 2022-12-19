class NubankCommons(object):
    def __init__(self):
        self.__CARD_STATEMENTS: str = 'nubank-card-statements'
        self.__ACCOUNT_FEED: str = 'nubank-account-feed'

    @property
    def CARD_STATEMENTS(self) -> str:
        return self.__CARD_STATEMENTS

    @property
    def ACCOUNT_FEED(self) -> str:
        return self.__ACCOUNT_FEED


NuCommons = NubankCommons()
