class botstru:

    config = {
        "variants": {
            "noauth": {
                "message": "Привет, {name}!",
                "contoller": "BotController",
                "contoller_action": "registration"  
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
                    "help": {
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
                            "users": {
                                "action": "Польз-ли",
                                "message": "Пользователи:",
                                "access": {"view": "admin"}, 
                                "variants": {
                                    "list": {
                                        "action": "Список",
                                        "message": "Список пользователей:",
                                        "contoller": "UsersController",
                                        "contoller_action": "list",    
                                        "access": {"view": "admin"}, 
                                    },
                                    "add_user": {
                                        "action": "Добавить",
                                        "message": "Добавить пользователя:",
                                        "contoller": "UsersController",
                                        "contoller_action": "add_user",    
                                        "access": {"view": "admin"}, 
                                    }
                                }    
                            },
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