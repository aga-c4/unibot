class main:

    config = {
        "system": {
            # Список id пользователей, которыt могут управлять доступом к боту
            "telegram_admin_ids": [], 
        },
        "bot": {
            # Название бота, будет присутствовать в сообщениях
            "name": "Demo",
            "start_hint": "Привет, {name}! Я Demo бот."
        },
        # Параметры для публикации сообщений в канал рассылки в Телеграм
        "telegram": {
            #AgaUniBot t.me/AgaUniBot
            "api_token": "",
            "channels": {
                "domchat": "-0000000000000"
            }
        },
        # Подключения к БД
        "db": {
            "default": {
                # MSSQL c использованием драйвера pyodbc
                "driver": "pyodbc",
                # Строка импорат драйвера
                "import_driver": "app.models.dbmssqlodbc", # Если драйвер свой, то можно указать так - "app.models.telegram"
                # Класс, драйвера
                "driver_class": "Dbmssqlodbc",
                # Количество кнопок на строке
                "init_params": {
                    # "host": '127.0.0.1',
                    # "port": '1435', 
                    # "user": 'DBUSER',
                    # "password": 'DBPASSWORD',
                    # "database": 'DBNAME',
                    # "autocommit": True,
                    # "use_mars": True
                },
                "timezone": "Europe/Moscow" 
            },
             "dbmssql": {
                # MSSQL c использованием драйвера pyodbc
                "driver": "pyodbc",
                # Строка импорат драйвера
                "import_driver": "app.models.dbmssql", # Если драйвер свой, то можно указать так - "app.models.telegram"
                # Класс, драйвера
                "driver_class": "MSSQLClient",
                # Количество кнопок на строке
                "init_params": {
                    # "host": '127.0.0.1',
                    # "port": '1435', 
                    # "user": 'DBUSER',
                    # "password": 'DBPASSWORD',
                    # "database": 'DBNAME',
                    # "autocommit": True,
                    # "use_mars": True
                },
                "timezone": "Europe/Moscow"  
            },
             "mysql": {
                # MSSQL c использованием драйвера pyodbc
                "driver": "mysql",
                # Строка импорат драйвера
                "import_driver": "app.models.dbmysql", # Если драйвер свой, то можно указать так - "app.models.telegram"
                # Класс, драйвера
                "driver_class": "Dbmysql",
                # Количество кнопок на строке
                "init_params": {
                    # "host": '127.0.0.1',
                    # "port": 3306,
                    # "user": "DBUSER",
                    # "passwd": "DBPASSWORD",
                    # "database": "DBNAME"
                },
                "timezone": "Europe/Moscow"  
            }
        }
    }
