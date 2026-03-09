class main:

    config = {
        "system": {
            # Путь к директории файлов на отдачу
            "out_path": "app/tmp/out",
            # Путь к директории файлов на прием
            "in_path": "app/tmp/in",
            # Путь к директории процессов бота
            "proc_path": "app/tmp/process",
            # Максимальное время исполнения процесса, после чего он будет считаться завершенным, 
            # даже если нет сведения об этом (sec)
            "proc_ttl": 2 * 60 * 60, 
            # Таймзона работы бота
            "timezone": "Europe/Moscow",
            # Список id пользователей, которыt могут управлять доступом к боту
            "telegram_admin_ids": [], 
            # Список допустимых ролей в системе
            "allow_roles": ["admin","manage","user"],
            # requests ttl (sec)
            "requests_ttl": 4,
            # Список доступных языков
            "available_langs": ["ru", "en"],
            # Дефолтовый язык
            "default_lang": "ru",
            # Драйвер месседжера
            "message_driver": "agaunibot.telegram"
        },
        "bot": {
            # Название бота, будет присутствовать в сообщениях
            "name": "Демо бот",
            # Количество кнопок на странице
            "btn_in_pg": 6,
            # Префикс кнопки предыдущей/следующей страницы
            "btn_pg_prefix": "pg",
            # Дефолтовая нода авторизованного пользователя без языка (он будет добавлен)
            "def_node": "main",
            # Дефолтовая нода авторизованного пользователя без языка (он будет добавлен)
            "def_node_noauth": "noauth",
            # Маршрут по умолчанию для неавторизованного пользователя всегда на дефолтовом языке
            "def_route": ["def_node"],
            # Маршрут по умолчанию для неавторизованного пользователя всегда на дефолтовом языке
            "def_route_noauth": ["def_node_noauth"],
            # Путь до моделей бота для загрузки модулей
            "bot_models_prefix": "app.models.",
            # Путь до сервисов бота для загрузки модулей
            "bot_controllers_prefix": "app.controllers.",
            # Наименование 3й кнопки общей навигации бота
            "nav_dop_variant": "Помощь",
            # Наименование кнопки "Главная" общей навигации бота
            "main_variant": "Главная",
            # Наименование кнопки "Вперед" общей навигации бота
            "forvard_variant":  "Вперед",
            # Наименование кнопки "Назад" общей навигации бота
            "back_variant": "Назад",
            # Наименование 3й кнопки общей навигации бота (пустая строка - не выводится)
            "nav_dop_variant": "Выход",
            # Маршрут 3й кнопки общей навигации бота
            "nav_dop_variant_route": ["def_node","logout"],
            # Наименование 3й кнопки общей навигации бота (пустая строка - не выводится)
            "nav_dop_variant_noauth": "Помощь",
            # Маршрут 3й кнопки общей навигации бота для неавторизованного пользователя
            "nav_dop_variant_route_noauth": ["def_node_noauth","help"],
            # Контроллер анализатора текстов бота, если не задан, то не вызывается
            "analyse_text_controller": "TextAnalyseController"
        },
        # Параметры модуля работы с мессенджерами
        "messages": {
            # Алиас используемого мессенджера, по нему подтянется конфиг
            "driver_alias": "telegram",
            # Строка импорат драйвера
            "import_driver": "agaunibot.telegram", # Если драйвер свой, то можно указать так - "app.models.telegram"
            # Класс, драйвера
            "driver_class": "Telegram",
            # Количество кнопок на строке
            "def_markup_row_width": 3
        },
        # Параметры для публикации сообщений в канал рассылки в Телеграм
        "telegram": { 
            "api_token": "",
            "channels": {
                "domchat": "-000000000000"
            }
        },
        # Подключения к БД
        "db": {
            "mssql1": {
                # MSSQL c использованием драйвера pyodbc
                "driver": "pyodbc",
                # Строка импорат драйвера
                "import_driver": ".pyodbc", # Если драйвер свой, то можно указать так - "app.models.telegram"
                # Класс, драйвера
                "driver_class": "MSSQLClient",
                # Количество кнопок на строке
                "init_params": {
                    "connection_string": (
                        "Driver={ODBC Driver 17 for SQL Server};"
                        "Server=localhost,1433;"
                        "Database=TestDB;"
                        "UID=sa;PWD=your_password"
                    )
                } 
            }
        }
    }

