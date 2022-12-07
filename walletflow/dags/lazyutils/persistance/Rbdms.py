import sqlalchemy as sa


class RBDMS:
    _engine = None
    _connection = None

    @property
    def engine(self):
        return self._engine

    @property
    def connection(self):
        return self._connection

    def __init__(self, connection_str: str):
        if connection_str is None or connection_str == '':
            raise Exception('Variable connection_str not provided')

        self._engine = sa.create_engine(connection_str)
        self._connection = self._engine.connect()

    def __del__(self):
        self.connection.close()
        self._engine.dispose()
