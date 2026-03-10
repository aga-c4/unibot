'''
Требует
pip install mysql-connector-python

config = {
    'db':{    
        'host': '127.0.0.1',
        'port': 3309,
        'user': 'dbuser',
        'passwd': 'dbpasswd',
        'db': 'dbname',
    }
}
db = Dbmysql(config['db'])

# Выполнение запроса SELECT
result = db.query("SELECT * FROM users")
for row in result:
    print(row)

# Выполнение запроса INSERT
new_user_id = db.insert("INSERT INTO users (name, email) VALUES (%s, %s)", ("John Doe", "johndoe@example.com"))
print("New user ID:", new_user_id)

# Выполнение запроса UPDATE
updated_rows = db.update("UPDATE users SET email = %s WHERE id = %s", ("newemail@example.com", 1))
print("Updated rows:", updated_rows)

# Выполнение запроса DELETE
deleted_rows = db.delete("DELETE FROM users WHERE id = %s", (1,))
print("Deleted rows:", deleted_rows)
'''

import logging
import mysql.connector

class Dbmysql:
    config_db = {}
    connection = None
    cursor = None
    autocommit = True

    
    def __init__(self, **config_db): 
        self.config_db = dict(config_db)
        self.autocommit = config_db.get("autocommit", True)
        self.connect()

    def connect(self):
        try:
            if 'host' in self.config_db: 
                if self.connection is None and type(self.config_db) is dict:
                    host=self.config_db.get('host', "")
                    port=self.config_db.get('port', 3306)
                    username=self.config_db.get('user', "")
                    password=self.config_db.get('password', "")
                    database=self.config_db.get('database', "")   
                    print("self.config_db:", self.config_db)    
                    self.connection = mysql.connector.connect(
                        host=host,
                        port=port,
                        username=username,
                        password=password,
                        database=database
                    )
                print("!!!")    
                if self.connection is not None:    
                    self.cursor = self.connection.cursor()
                    return True    
            return False
        except Exception as e:
            logging.error(f"MySQL(Dbmysql) connect error: {e}")
            self.ping()
            return False      
    
    def _ensure_connected(self) -> None:
        if self.connection is None:
            self.connect()
    
    def execute(self, sql, params=None):
        self._ensure_connected()
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            if self.autocommit:    
                self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            logging.error(f"MySQL(Dbmysql) execute error: {e}")
            self.ping()
            return None
        
    def query(self, sql, params=None, dictionary:bool=True):
        """Создает и возвращает новый курсор (None в случае ошибки), не забывайте закрывать cursor.close()"""
        self._ensure_connected()
        try:
            if dictionary:
                cursor = self.connection.cursor(dictionary=True)
            else:
                cursor = self.connection.cursor()    

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)   
            return cursor
        except Exception as e:
            logging.error(f"MySQL(Dbmysql) query error: {e}")
            self.ping()
            return None

    def fetchall(self, sql, params=None, dictionary:bool=True):
        self._ensure_connected()
        try:
            cursor = self.cursor
            if dictionary:
                cursor = self.connection.cursor(dictionary=True)

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)   
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"MySQL(Dbmysql) fetchall error: {e}")
            self.ping()
            return None
    
    def fetch_one(self, sql, params=None, dictionary:bool=True):
        self._ensure_connected()
        try:
            cursor = self.cursor
            if dictionary:
                cursor = self.connection.cursor(dictionary=True)

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)   
            return cursor.fetch_one()
        except Exception as e:
            logging.error(f"MySQL(Dbmysql) fetch_one error: {e}")
            self.ping()
            return None
    

    def insert(self, sql, params=None):
        self._ensure_connected()
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            if self.autocommit:    
                self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logging.error(f"MySQL(Dbmysql) insert error: {e}")
            self.ping()
            return None

    def update(self, sql, params=None):
        self._ensure_connected()
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            if self.autocommit:    
                self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            logging.error(f"MySQL(Dbmysql) update error: {e}")
            self.ping()
            return None

    def delete(self, sql, params=None):
        self._ensure_connected()
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            if self.autocommit:    
                self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            logging.error(f"MySQL(Dbmysql) delete error: {e}")
            self.ping()
            return None
        

    @staticmethod
    def close_cursor(cursor):
        '''Закрывает курсор'''
        try:
            return cursor.close()
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) close_cursor error: {e}")
            return None     

    def begin(self) -> None:
        """Начать транзакцию (если autocommit=False)."""
        # TODO - Вероятно не будет нормально работать при разделении объекта self.connection между процессами
        if self.connection and self.autocommit:
            self.autocommit = False
        try:
            if hasattr(self.connection, "begin"):
                self.connection.start_transaction()
                return True
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) begin error: {e}")
            self.ping()        
            return False

    def commit(self) -> None:
        """Зафиксировать транзакцию."""
        # TODO - Вероятно не будет нормально работать при разделении объекта self.connection между процессами
        self._ensure_connected()
        try:
            if hasattr(self.connection, "commit"):
                self.connection.commit()
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"MSSQL(MSSQLClient) commit error: {e}")
            self.ping()        
            return False        

    def rollback(self) -> None:
        """Откатить транзакцию."""
        # TODO - Вероятно не будет нормально работать при разделении объекта self.connection между процессами
        self._ensure_connected()
        try:
            if hasattr(self.connection, "rollback"):
                self.connection.rollback()
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
    
    def __del__(self):
        try:
            self.cursor.close()
            self.connection.close()
        except:
            pass

    def ping(self)->bool:
        """Проверяет соединение с сервером. Если оно утеряно, автоматически предпринимается попытка пересоединения.
            Возвращает - TRUE, если соединение в рабочем состоянии и FALSE в противном случае."""
        
        try:
            if self.connection is not None: 
                logging.info("MSSQL(Dbmssqlodbc) try to reconnect:")
                self.connection.ping(reconnect=True, attempts=3, delay=0)
                # При недоступности соединения будет поднята ошибка InterfaceError
                return True
            else: 
                return False
        except Exception as e:
            logging.error(f"MSSQL(Dbmssqlodbc) Error: {e}")
            self.close()
            return False    
