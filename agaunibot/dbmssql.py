'''
Требует
pip install mssql_python
Полезные ссылки:
https://www.iditect.com/faq/python/how-to-use-multiple-cursors-on-one-connection-with-pyodbc-and-ms-sql-server.html?ysclid=mmgv4foc8l216350511
https://proglib.io/p/rabotaem-s-sql-server-s-pomoshchyu-python-2020-04-18?ysclid=mm95t36nqw307579915
'''
# TODO - разобраться с работой с одним объектом разных потоков исполнения, возможны проблемы с транзакциями

from typing import Any, List, Optional, Tuple, Dict
import logging

# Попытка импортировать библиотеку mssql-python
try:
    from mssql_python import connect  # предположительное API
except Exception:
    connect = None  # чтобы код не падал на импорте, если библиотека не установлена

logger = logging.getLogger(__name__)

class MSSQLClient:
    """
    Обёртка поверх библиотеки mssql-python для MSSQL.
    Поддерживает подключение, выполнение запросов, транзакции и безопасное закрытие.
    """

    use_mars = False

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        use_mars: bool = False, # Multiple Active Result Sets (MARS) - при подключении устанавливает MultipleActiveResultSets=Yes
        autocommit: bool = True,
        connection_string: Optional[str] = None, # Если задана, то используется вместо настроек подключения к базе (максимальный приоритет)
        *args, **kwargs
    ):
        """
        Инициализация клиента.
        Можно явно передать параметры подключения или использовать connection_string.
        """

        self.autocommit = autocommit
        self._conn = None
        self._cursor = None

        if connect is None:
            raise RuntimeError("mssql-python не установлен или не распознан импорт. Установите пакет mssql-python.")

        if connection_string:
            self.connection_string = connection_string
        else:
            parts = []
            if host:
                parts.append(f"host={host}")
            if port:
                parts.append(f"port={port}")
            if database:
                parts.append(f"database={database}")
            if user:
                parts.append(f"user={user}")
            if password:
                parts.append(f"password={password}")
            if use_mars:
                    self.use_mars = True
                    parts.append(f"MultipleActiveResultSets=Yes")       
            if options:
                for k, v in options.items():
                    parts.append(f"{k}={v}")
            self.connection_string = ";".join(parts)
        self.connect()    

    def connect(self) -> None:
        """Установить соединение с базой."""
        try:
            if self._conn is not None:
                return self.ping()
            self._conn = connect(self.connection_string)
            # предположим, что MSSQL возвращает объект соединения, можно получить курсор
            self._cursor = self._conn.cursor()
            # Установка автокоммита, если поддерживается
            if hasattr(self._conn, "set_autocommit"):
                self._conn.set_autocommit(self.autocommit)
            return True
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) connect error: {e}")
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
        """
        self._ensure_connected()
        try:
            if params:
                res = self._cursor.execute(query, params)
            else:
                res = self._cursor.execute(query)
            # Если API возвращает количество затронутых строк, применяем
            return getattr(res, "rowcount", 0)
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) execute error: {e}")
            self.ping()
            return None
    
    def query(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> int:
        """
        Выполнить запрос c возвратом результата (SELECT,...) для дальнейшего построчного разбора.
        Создает и возвращает новый курсор (None в случае ошибки), не забывайте закрывать cursor.close()
        Требует use_mars=True при коннекте к базе.
        """
        self._ensure_connected()
        try:
            if params:
                res = self._cursor.execute(query, params)
            else:
                res = self._cursor.execute(query)
            # Если API возвращает количество затронутых строк, применяем
            return res
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) query error: {e}")
            self.ping()
            return None

    def fetch_all(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Tuple]:
        """Выполнить SELECT и вернуть все строки."""
        self._ensure_connected()
        try:
            if params:
                cur = self._cursor.execute(query, params)
            else:
                cur = self._cursor.execute(query)
            return cur.fetchall()
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) fetch_all error: {e}")
            self.ping()
            return None

    def fetch_one(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Tuple]:
        """Выполнить SELECT и вернуть одну строку или None."""
        self._ensure_connected()
        try:
            if params:
                cur = self._cursor.execute(query, params)
            else:
                cur = self._cursor.execute(query)
            return cur.fetchone()
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) fetch_one error: {e}")
            self.ping()
            return None
    
    @staticmethod
    def fetchmany(sqlres, size:int=1):
        '''Возвратит список значений, не более чем size единиц, если возвращать нечего, вернет пустой список'''
        try:
            res = sqlres.fetchmany(size)
            if type(res) is list and len(res)>0:
                return sqlres.fetchmany(size)
            else: return None
        except:
            return None

    @staticmethod
    def nextset(cursor):
        '''Переходит к следующему датасету, если такой не найден, возвращает False'''
        try:
            return cursor.nextset()
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) nextset error: {e}")
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
        """Массовая вставка/обновление."""
        self._ensure_connected()
        try:
            res = self._cursor.executemany(query, seq_of_params)
            return getattr(res, "rowcount", 0)
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) executemany error: {e}")
            self.ping()
            return None

    def begin(self) -> None:
        """Начать транзакцию (если autocommit=False)."""
        # TODO - Вероятно не будет нормально работать при разделении объекта self._conn между процессами
        self._ensure_connected()
        try:
            self._ensure_connected()
            if self._conn and self.autocommit:
                self._conn.autocommit = False    
                self._conn.set_autocommit(self.autocommit)
            if hasattr(self._conn, "begin"):
                self._conn.begin()
                return True
            return False
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) begin error: {e}")
            self.ping()        
            return False

    def commit(self) -> None:
        """Зафиксировать транзакцию."""
        # TODO - Вероятно не будет нормально работать при разделении объекта self._conn между процессами
        self._ensure_connected()
        try:
            if hasattr(self._conn, "commit"):
                self._conn.commit()
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) commit error: {e}")
            self.ping()        
            return False

    def rollback(self) -> None:
        """Откатить транзакцию."""
        # TODO - Вероятно не будет нормально работать при разделении объекта self._conn между процессами
        self._ensure_connected()
        try:
            if hasattr(self._conn, "rollback"):
                self._conn.rollback()
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) rollback error: {e}")
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
    # Способ 1: через параметры подключения
    client = MSSQLClient(
        host="localhost",
        port=1433,
        user="sa",
        password="your_password",
        database="TestDB",
        autocommit=False,
    )
    try:
        client.connect()
        for row in client.fetch_all("SELECT TOP 5 id, name FROM employees"):
            print(row)

        client.execute("INSERT INTO employees (name, position) VALUES (?, ?)", ("Иван", "Разработчик"))
        client.commit()
    finally:
        client.close()

