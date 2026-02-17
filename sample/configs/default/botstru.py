class botstru:

    config = {
        "variants": {
            "noauth": {
                "message": "Привет, {name}! Я Demo бот.",
                "access": {"view": "noroles"},   
                "variants": {
                    "authorization": {
                        "action": "Авторизация",
                        "message": "Авторизация:",
                        "contoller": "BotController",
                        "contoller_action": "authorization",
                        "access": {"view": "noroles"}
                    },
                    "registration": {
                        "action": "Регистрация",
                        "message": "Регистрация:",
                        "contoller": "BotController",
                        "contoller_action": "registration",
                        "access": {"view": "noroles"}   
                    },
                    "help": {
                        "action": "Помощь",
                        "message": "Авторизуйтесь или Зарегистрируйтесь для начала работы с системой",
                        "access": {"view": "noroles"},    
                    },    
                },  
            },    
            "main": {
                "message": "Главная:",
                "access": {"view": "user"},
                "variants": {
                    "info": {
                        "action": "Инфо",
                        "message": "Инфо:",
                        "contoller": "DemoController",
                        "contoller_action": "get_info",   
                        "access": {"view": "user"},    
                    },
                    "demomess": {
                        "action": "Сообщение",
                        "message": "Отправка в канал:",
                        "contoller": "DemoController",
                        "contoller_action": "send_to_canal",   
                        "access": {"view": "user"},    
                    },
                    "helpauth": {
                        "action": "Помощь",
                        "message": "Помощь:",
                        "contoller": "BotController",
                        "contoller_action": "help",   
                        "access": {"view": "user"},    
                    },
                    "settings": {
                        "action": "Настройки",
                        "message": "Настройки:",
                        "access": {"view": "admin"}, 
                        "variants": {
                            "getip": {
                                "action": "IP адрес",
                                "message": "IP адрес бота:",
                                "contoller": "BotController",
                                "contoller_action": "get_ip",    
                                "access": {"view": "admin"}, 
                            }
                        }
                    }
                }   
            }             
        }
    }    