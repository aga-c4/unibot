import logging

from agaunibot.request import Request
from agaunibot.message import Message

class BotController:

    def get_map(self, request:Request):
        logging.info(str(request.user.id)+": BotController:bot_map")    
        message = Message(request.bot.config["telegram"])   
        def_route = request.bot.def_route
        node = request.bot.get_node_by_route(lang=request.lang, def_route=def_route)   
        for vi1,item1 in node["variants"].items():
            if vi1!="map":
                route = request.bot.def_route[:]
                route.append(vi1)
                message.add_markup([{"text":item1["action"], "command":'.'.join(route)}])
                if "variants" in item1:
                    items_list = []
                    for vi2,item2 in item1["variants"].items():
                        if vi2!="map":
                            route2 = route[:]
                            route2.append(vi2)
                            items_list.append({"text":item2["action"], "command":'.'.join(route2)})
                    message.add_markup(items_list)
                message.send(request.chatid, text=">")    

    def get_ip(self, request:Request):
        logging.info(str(request.user.id)+": BotController:get_ip")  
        message = Message(request.bot.config["telegram"])    
        mess_txt = request.bot.get_ip()
        message.send(request.chatid, text=mess_txt) 

    def registration(self, request:Request):
        logging.info(str(request.user.id)+": BotController:registration")  
        message = Message(request.bot.config["telegram"])     
        mess_data = request.bot.get_data_from_message(request.message)

        if request.is_script_command and mess_data["command"]=="registration": 
            message.edit_message_text(request.message.from_user.id, 
                                        message_id=request.message.message.message_id, 
                                        new_text=_("Сообщите администратору идентификатор, который вы увидите"),
                                        reply_markup=None) 
            message.send(request.chatid, text=_("Ваш идентификатор: ") + str(request.user.id))                
        else:    
            logging.info("command: "+request.route_str+":registration")  
            message.add_markup([{"text":_("Зарегистрироваться"), "command":request.route_str+":registration"}])   
            message.send(request.chatid, text=_("Авторизуйтесь или зарегистрируйтесь для начала работы с системой")) 

    def authorization(self, request:Request):
        logging.info(str(request.user.id)+": BotController:authorization")  
        message = Message(request.bot.config["telegram"])   
        mess_data = request.bot.get_data_from_message(request.message, request.route_data)
        if mess_data["text"]!=_("Авторизация") and mess_data["text"]!="":
            if mess_data["text"]=="password":
                udata = {
                    "id": request.user.id,
                    "params": {},
                    "roles": ["user"],
                    "lang": "",
                    "exist": False,
                    "is_root": False
                }
                request.session.up()
                request.user.set_data(udata)
                request.session.set({"user_data": udata})
                request.session.set({"user_auth": True})
                request.user.set_data(udata)
                logging.info(str(request.user.id) + f": redirect to []")  
                return {"redirect": {"route":[]}}
            else:     
                message.send(request.chatid, text=_("Пароль не найден!") + str(request.user.id))                
        else: 
            # Смотрим админа в конфиге и пользователей в файле, если не находим, то предлагаем ввести пароль 
            udata = request.user.get_user_info() 
            if udata.get("exist", False):
                request.session.up()
                request.user.set_data(udata)
                request.session.set({"user_data": udata})
                request.session.set({"user_auth": True})
                logging.info(str(request.user.id) + f": redirect to []")  
                return {"redirect": {"route":[]}}
            else:    
                message.send(request.chatid, text=_("Введите пароль:"))             

    def help(self, request:Request):
        logging.info(str(request.user.id)+": BotController:help")  
        message = Message(request.bot.config["telegram"])    
        mess_txt = _("AUTH: Это демо пример работы фреймворка, на базе которого можно создать телеграм бота.")
        message.send(request.chatid, text=mess_txt)         

    def logout(self, request:Request):
        logging.info(str(request.user.id)+": BotController:logout")  
        message = Message(request.bot.config["telegram"])    
        mess_txt = _("Вы вышли из системы")
        message.send(request.chatid, text=mess_txt)  
        udata = {
            "id": request.user.id,
            "params": {},
            "roles": [],
            "lang": "",
            "exist": False,
            "is_root": False
        }
        request.session.up()
        request.user.set_data(udata)
        request.session.delete()
        logging.info(str(request.user.id) + f": logout")  
        return {"redirect": {"route":[]}}       