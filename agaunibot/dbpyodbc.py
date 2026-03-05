import pyodbc
from typing import Any, List, Optional, Tuple, Dict

class MSSQLClient:
    """
    Простое обертка над pyodbc для работы с MSSQL.
    Подключение через DSN или строку подключения.
    """
    def __init__(
        self,
        connection_string: Optional[str] = None,
        dsn: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
        database: Optional[str] = None,
        driver: str = "ODBC Driver 17 for SQL Server",
        port: Optional[int] = None,
        autocommit: bool = False,
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация клиента.
        Можно либо передать connection_string, либо собрать строку подключения из параметров.
        """
        self.autocommit = autocommit
        self._conn: Optional[pyodbc.Connection] = None
        self._cursor: Optional[pyodbc.Cursor] = None

        if connection_string:
            self.connection_string = connection_string
        else:
            # сборка строки подключения
            parts = []
            if dsn:
                parts.append(f"DSN={dsn}")
            else:
                if server:
                    parts.append(f"Server={server}")
                if port:
                    parts.append(f"Port={port}")
                if database:
                    parts.append(f"Database={database}")
                # драйвер можно переопределить извне
                parts.append(f"Driver={{{driver}}}")
                if username:
                    parts.append(f"UID={username}")
                if password:
                    parts.append(f"PWD={password}")
            if options:
                for k, v in options.items():
                    parts.append(f"{k}={v}")
            self.connection_string = ";".join(parts)

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

# Пример использования
if __name__ == "__main__":
    # Способ 1: через строку подключения
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost,1433;"
        "Database=TestDB;"
        "UID=sa;PWD=your_password"
    )
    client = MSSQLClient(connection_string=conn_str, autocommit=False)
    try:
        client.connect()
        # пример чтения
        for row in client.fetch_all("SELECT TOP 5 id, name FROM employees"):
            print(row)

        # пример вставки
        client.execute("INSERT INTO employees (name, position) VALUES (?, ?)", ("Иван", "Разработчик"))
        client.commit()
    finally:
        client.close()

        