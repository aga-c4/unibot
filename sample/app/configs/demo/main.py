class main:

    config = {
        "system": {
            # Список id пользователей, которыt могут управлять доступом к боту
            "telegram_admin_ids": [], 
        },
        "bot": {
            # Название бота, будет присутствовать в сообщениях
            "name": "Demo",
            "start_hint": "Привет, {name}! Я Demo бот.",
            # Контроллер анализатора текстов бота, если не задан, то не вызывается
            "analyse_text_controller": "TextAnalyseController"
        },
        # Параметры для публикации сообщений в канал рассылки в Телеграм
        "telegram": {
            #AgaUniBot t.me/AgaUniBot
            "api_token": "",
            "channels": {
                "domchat": "-0000000000000"
            }
        }
    }
