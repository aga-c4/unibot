'''
Требует
pip install pyodbc
Полезные ссылки:
https://learn.microsoft.com/ru-ru/sql/connect/python/mssql-python/python-sql-driver-mssql-python-quickstart?view=sql-server-ver17&tabs=windows%2Cazure-sql
'''
# TODO - разобраться с работой с одним объектом разных потоков исполнения, возможны проблемы с транзакциями

import logging
import pyodbc
from typing import Any, List, Optional, Tuple, Dict

class Dbmssqlodbc:
    """
    Простое обертка над pyodbc для работы с MSSQL.
    Подключение через DSN или строку подключения.
    """
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        autocommit: bool = True,
        driver: str = "ODBC Driver 17 for SQL Server",
        use_mars: bool = False, # Multiple Active Result Sets (MARS) - при подключении устанавливает MultipleActiveResultSets=Yes
        connection_string: Optional[str] = None, # Если задана, то используется вместо настроек подключения к базе (максимальный приоритет)
        dsn: Optional[str] = None, # Если задана, то используется вместо настроек подключения к базе с использованием options
        *args, **kwargs
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
                if host:
                    parts.append(f"Server={host}")
                if port:
                    parts.append(f"Port={port}")
                if database:
                    parts.append(f"Database={database}")
                # драйвер можно переопределить извне
                parts.append(f"Driver={{{driver}}}")
                if user:
                    parts.append(f"UID={user}")
                if password:
                    parts.append(f"PWD={password}")
                if use_mars:
                    self.use_mars = True
                    parts.append(f"MultipleActiveResultSets=Yes")       
            if options:
                for k, v in options.items():
                    parts.append(f"{k}={v}")
            self.connection_string = ";".join(parts)   
        self.connect()
        
    def connect(self) -> bool:
        """Установить соединение с базой."""
        try:
            if self._conn is not None:
                return self.ping()
            self._conn = pyodbc.connect(self.connection_string, autocommit=self.autocommit)
            if self.use_mars:
                # Enabling Multiple Active Result Sets (MARS)
                self._conn.set_attr(pyodbc.SQL_ATTR_MARS_ENABLED, True)     
            self._cursor = self._conn.cursor()
            return True
        except Exception as e:
            logging.error(f"MSSQL(Dbmssqlodbc) connect error: {e}")
            self.ping()
            return False    

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
        res.rowcount содержит количество записей
        """
        self._ensure_connected()
        try:
            if params:
                res = self._cursor.execute(query, params)
            else:
                res = self._cursor.execute(query)
            return res.rowcount
        except Exception as e:
            logging.error(f"MSSQL(Dbmssqlodbc) execute error: {e}")
            self.ping()
            return None


    def query(self, query: str, params: Optional[Tuple[Any, ...]] = None):
        """
        Выполнить запрос c возвратом результата (SELECT,...) для дальнейшего построчного разбора.
        Создает и возвращает новый курсор (None в случае ошибки), не забывайте закрывать cursor.close()
        Требует use_mars=True при коннекте к базе.
        """
        self._ensure_connected()
        try:
            cursor = self._conn.cursor()
            if params:
                res = cursor.execute(query, params)
            else:
                res = cursor.execute(query)
            return cursor
        except Exception as e:
            logging.error(f"MSSQL(Dbmssqlodbc) query error: {e}")
            self.ping()
            return None


    def fetch_all(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Tuple]:
        """
        Выполнить SELECT и вернуть все строки.
        """
        self._ensure_connected()
        try:
            if params:
                cur = self._cursor.execute(query, params)
            else:
                cur = self._cursor.execute(query)
            return cur.fetchall()
        except Exception as e:
            logging.error(f"MSSQL(Dbmssqlodbc) fetch_all error: {e}")
            self.ping()
            return None

    def fetch_one(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Tuple]:
        """
        Выполнить SELECT и вернуть одну строку или None.
        """
        self._ensure_connected()
        try:
            if params:
                cur = self._cursor.execute(query, params)
            else:
                cur = self._cursor.execute(query)
            return cur.fetchone()
        except Exception as e:
            logging.error(f"MSSQL(Dbmssqlodbc) fetch_one error: {e}")
            self.ping()
            return None
    
    @staticmethod
    def fetchmany(cursor, size:int=1):
        '''Возвратит список значений, не более чем size единиц, если возвращать нечего, вернет пустой список'''
        try:
            res = cursor.fetchmany(size)
            if type(res) is list and len(res)>0:
                return cursor.fetchmany(size)
            else: return None
        except:
            return None

    @staticmethod
    def nextset(cursor):
        '''Переходит к следующему датасету, если такой не найден, возвращает False'''
        try:
            return cursor.nextset()
        except Exception as e:
            logging.error(f"MSSQL(Dbmssqlodbc) nextset error: {e}")
            return None

    @staticmethod
    def close_cursor(cursor):
        '''Закрывает курсор'''
        try:
            return cursor.close()
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) close_cursor error: {e}")
            return None             

    def executemany(self, query: str, seq_of_params: List[Tuple[Any, ...]]) -> int:
        """
        Выполнить массовую вставку/обновление.
        Возвращает количество операций.
        """
        self._ensure_connected()
        try:
            res = self._cursor.executemany(query, seq_of_params)
            return res.rowcount
        except Exception as e:
            logging.error(f"MSSQL(Dbmssqlodbc) executemany error: {e}")
            self.ping()
            return None

    def begin(self) -> None:
        """Начать транзакцию (если autocommit=False)."""
        # TODO - Вероятно не будет нормально работать при разделении объекта self._conn между процессами
        try:
            self._ensure_connected()
            if self._conn and self.autocommit:
                self._conn.autocommit = False
                self.close()
                self.connect()
            return True
        except Exception as e:
            logging.error(f"MSSQL(Dbmssqlodbc) begin error: {e}")
            self.ping()        
            return False

    def commit(self) -> None:
        """Зафиксировать транзакцию."""
        # TODO - Вероятно не будет нормально работать при разделении объекта self._conn между процессами
        self._ensure_connected()
        try:
            if self._conn:
                self._conn.commit()
            else:    
                return False
        except Exception as e:
            logging.error(f"MSSQL(Dbmssqlodbc) commit error: {e}")
            self.ping()        
            return False

    def rollback(self) -> None:
        """Откатить транзакцию."""
        # TODO - Вероятно не будет нормально работать при разделении объекта self._conn между процессами
        self._ensure_connected()
        try:
            if self._conn:
                self._conn.rollback()
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"MSSQL(Dbmssqlodbc) rollback error: {e}")
            self.ping()        
            return False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()
        return False
    
    def ping(self)->bool:
        """Проверяет соединение с сервером. Если оно утеряно, автоматически предпринимается попытка пересоединения.
            Возвращает - TRUE, если соединение в рабочем состоянии и FALSE в противном случае."""
        
        try:
            if self._conn is not None: 
                logging.info("MSSQL(Dbmssqlodbc) try to reconnect:")
                self._conn.ping(reconnect=True, attempts=3, delay=0)
                # При недоступности соединения будет поднята ошибка InterfaceError
                return True
            else: 
                return False
        except Exception as e:
            logging.error(f"MSSQL(Dbmssqlodbc) Error: {e}")
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
    client = Dbmssqlodbc(connection_string=conn_str, autocommit=False)
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

        