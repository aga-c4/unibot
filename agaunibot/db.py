'''
Фасад для работы с базами данных, реализует паттерн мультисинглтон, когда
в параметр создания объекта передается алиас настройки, а обратно возвращается
ссылка на объект для работы с базой, описанной в заданной настройке. 
Для каждой настройки создается только одна база. Таким образом мы можем 
одновременно использовать разные базы с разными драйверами, пользуясь при этом
всеми преимуществами синглтона. Если не задано, то дефолтная настройка - "default"
'''

import logging

class DB:

    def __init__(self):
        # Способ 1: через строку подключения
        conn_str = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost,1433;"
            "Database=TestDB;"
            "UID=sa;PWD=your_password"
        )
        client = MSSQLClient(connection_string=conn_str, autocommit=False)

    def connect(self) -> None:
        """Установить соединение с базой."""
        if self._conn is not None:
            return
        self._conn = pyodbc.connect(self.connection_string, autocommit=self.autocommit)
        self._cursor = self._conn.cursor()

    def close(self) -> None:
        """Закрыть курсор и соединение."""
        try:
            if self._cursor:
                self._cursor.close()
        finally:
            if self._conn:
                self._conn.close()
            self._cursor = None
            self._conn = None

    def _ensure_connected(self) -> None:
        if self._conn is None:
            self.connect()

    def execute(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> int:
        """
        Выполнить запрос без возврата результатов (INSERT/UPDATE/DELETE).
        Возвращает количество затронутых строк.
        """
        self._ensure_connected()
        if params:
            res = self._cursor.execute(query, params)
        else:
            res = self._cursor.execute(query)
        return res.rowcount

    def fetch_all(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Tuple]:
        """
        Выполнить SELECT и вернуть все строки.
        """
        self._ensure_connected()
        if params:
            cur = self._cursor.execute(query, params)
        else:
            cur = self._cursor.execute(query)
        return cur.fetchall()

    def fetch_one(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Tuple]:
        """
        Выполнить SELECT и вернуть одну строку или None.
        """
        self._ensure_connected()
        if params:
            cur = self._cursor.execute(query, params)
        else:
            cur = self._cursor.execute(query)
        return cur.fetchone()

    def executemany(self, query: str, seq_of_params: List[Tuple[Any, ...]]) -> int:
        """
        Выполнить массовую вставку/обновление.
        Возвращает количество операций.
        """
        self._ensure_connected()
        res = self._cursor.executemany(query, seq_of_params)
        return res.rowcount

    def begin(self) -> None:
        """Начать транзакцию (если autocommit=False)."""
        self._ensure_connected()
        if self._conn and self.autocommit:
            self._conn.autocommit = False

    def commit(self) -> None:
        """Зафиксировать транзакцию."""
        self._ensure_connected()
        if self._conn:
            self._conn.commit()

    def rollback(self) -> None:
        """Откатить транзакцию."""
        self._ensure_connected()
        if self._conn:
            self._conn.rollback()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            try:
                self.rollback()
            except Exception:
                pass
        else:
            try:
                self.commit()
            except Exception:
                pass
        self.close()
        return False
