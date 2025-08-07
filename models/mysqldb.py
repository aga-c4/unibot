'''
config = {
    'db':{    
        'host': '127.0.0.1',
        'port': 3309,
        'db': 'dbname',
        'user': 'dbuser',
        'passwd': 'dbpasswd'
    }
}
db = Mysqldb(config['db'])

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

import mysql.connector

class Mysqldb():
    mysql_objects = {}
    config_db = {}
    connection = None
    cursor = None
    db_alias = 'main'

    def connect(self, action:str='connect'):
        'action: connect | reconnect'
        if 'host' in self.config_db:
            if action!='connect' or self.connection is None:
                self.connection = mysql.connector.connect(
                    host=self.config_db['host'],
                    port=self.config_db['port'],
                    username=self.config_db['user'],
                    password=self.config_db['passwd'],
                    database=self.config_db['db']
                )
                self.cursor = self.connection.cursor()
                Mysqldb.mysql_objects[self.db_alias]['connection'] = self.connection
                Mysqldb.mysql_objects[self.db_alias]['cursor'] = self.cursor
            return True    
        return False
    
    
    def __init__(self, config_db:dict, db_alias:str='main'):
        if not db_alias in Mysqldb.mysql_objects:
            Mysqldb.mysql_objects[db_alias] = {'config_db': dict(config_db), 'connection': None, 'cursor': None}    

        self.db_alias = db_alias    
        self.config_db = Mysqldb.mysql_objects[db_alias]['config_db']    
        self.connection = Mysqldb.mysql_objects[db_alias]['connection']
        self.cursor = Mysqldb.mysql_objects[db_alias]['cursor']
        self.connect()


    def query(self, sql, params=None, dictionary:bool=True):
        cursor = self.cursor
        if dictionary:
            cursor = self.connection.cursor(dictionary=True)

        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)   
        return cursor.fetchall()

    def insert(self, sql, params=None):
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        self.connection.commit()
        return self.cursor.lastrowid

    def update(self, sql, params=None):
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        self.connection.commit()
        return self.cursor.rowcount

    def delete(self, sql, params=None):
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        self.connection.commit()
        return self.cursor.rowcount

    def __del__(self):
        pass
        # self.cursor.close()
        # self.connection.close()
