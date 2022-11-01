from walletflow.dags.common_package.secrets.SecretsException import SecretsNotFoundException


class Secrets:
    _user: str = None
    _pass: str = None
    _token: str = None

    def load(self):
        pass

    def _first_load(self):
        self.load()

        if self._user is None and self._pass is None and self._token is None:
            raise SecretsNotFoundException

    @property
    def user(self) -> str:
        if self._user is None:
            self._first_load()
        return self._user

    @property
    def password(self) -> str:
        if self._pass is None:
            self._first_load()
        return self._pass

    @property
    def token(self) -> str:
        if self._token is None:
            self._first_load()
        return self._token
