class botstru:

    config = {
        "variants": {
            "noauth_ru": {
                "message": "Привет, {name}! Я Demo бот.",
                "access": {"view": "noroles"},   
                "if_auth_redirect": ["def_node"],
                "variants": {
                    "authorization": {
                        "action": "Авторизация",
                        "message": "Авторизация:",
                        "access": {"view": "noroles"},
                        "if_auth_redirect": ["def_node"],
                        "contoller": "BotController",
                        "contoller_action": "authorization"
                    },
                    "registration": {
                        "action": "Регистрация",
                        "message": "Регистрация:",
                        "access": {"view": "noroles"},
                        "if_auth_redirect": ["def_node"],
                        "contoller": "BotController",
                        "contoller_action": "registration"  
                    },
                    "help": {
                        "action": "Помощь",
                        "message": "Авторизуйтесь или Зарегистрируйтесь для начала работы с системой",
                        "access": {"view": "noroles"},
                        "fast_back": True      
                    }    
                } 
            },    
            "main_ru": {
                "message": "Главная:",
                "access": {"view": "user"},
                "variants": {
                    "info": {
                        "action": "Инфо",
                        "message": "Инфо:",
                        "contoller": "DemoController",
                        "contoller_action": "get_info",   
                        "access": {"view": "user"},
                        "fast_back": True        
                    },
                    "demomess": {
                        "action": "Сообщение",
                        "message": "Отправка в канал:",
                        "contoller": "DemoController",
                        "contoller_action": "send_to_channel",   
                        "access": {"view": "user"},
                        "fast_back": True       
                    },
                    "help": {
                        "action": "Помощь",
                        "menu_hide": True,
                        "message": "Помощь:",
                        "contoller": "BotController",
                        "contoller_action": "help",   
                        "access": {"view": "user"},
                        "fast_back": True    
                    },
                    "logout": {
                        "action": "Помощь",
                        "menu_hide": True,
                        "message": "Помощь:",
                        "contoller": "BotController",
                        "contoller_action": "logout",   
                        "access": {"view": "user"},
                        "fast_back": True    
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
                                "fast_back": True     
                            }
                        }
                    }
                }   
            },
            "main_en": {
                "message": "Main:",
                "access": {"view": "user"},
                "variants": {
                    "info": {
                        "action": "Info",
                        "message": "Info:",
                        "contoller": "DemoController",
                        "contoller_action": "get_info",   
                        "access": {"view": "user"},    
                    },
                    "demomess": {
                        "action": "Message",
                        "message": "Send to channel:",
                        "contoller": "DemoController",
                        "contoller_action": "send_to_channel",   
                        "access": {"view": "user"},    
                    },
                    "helpauth": {
                        "action": "Help",
                        "message": "Help:",
                        "contoller": "BotController",
                        "contoller_action": "help",   
                        "access": {"view": "user"},    
                    },
                    "settings": {
                        "action": "Settings",
                        "message": "Settings:",
                        "access": {"view": "admin"}, 
                        "variants": {
                            "getip": {
                                "action": "IP addr",
                                "message": "IP bot addr:",
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