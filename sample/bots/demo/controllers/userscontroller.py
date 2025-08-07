from models.request import Request
import logging

from models.message import Message
from models.user import User

class UsersController:
    
    def list(self, request:Request):
        logging.info(str(request.user.id)+": UserController:list")
        message = Message(request.bot.config["telegram"])
        command = ""
        command_obj = ""
        command_info = ""
        if hasattr(request.message, "data"):
            command, command_obj, command_info = request.bot.get_dev_comm_by_str(request.message.data)

        # if request.same_route:
        #     logging.info(str(request.user.id)+": UserController:list:same_route")
        # el
        if request.is_script_command and command=="setrole":

            role = str(command_obj).lower()
            user_id = str(command_info)
            user = User(request.bot.conf_obj, user_id)
            if user.has_role(role,"all"):
                user.del_role(role)
            else:
                user.add_role(role)        

            # Проапдейтим сообщение из которого нажимали кнопку
            userdata = user.data
            username = userdata.get("params", {}).get("username","")
            first_name = userdata.get("params", {}).get("first_name","")
            last_name = userdata.get("params", {}).get("last_name","")
            language_code = userdata.get("params", {}).get("language_code","")
            is_bot = userdata.get("params", {}).get("is_bot", False)
            
            mess_txt = "id: " + user_id
            if is_bot:
                mess_txt += " (BOT)"
            mess_txt += " "+language_code+"\n"
            mess_txt += "username: " + username + "\n"   
            mess_txt += "first_name: " + first_name + "\n"
            if last_name!="":
                mess_txt += "last_name: " + last_name + "\n"   
            mess_txt += "roles: " + ", ".join(userdata["roles"]) + "\n"

            markup_list = []
            for role in request.bot.config["system"]["allow_roles"]:
                markup_list.append({"text":role, "command":request.route_str+":setrole:"+role+":"+user_id})
            markup_list.append({"text":"Удалить", "command":request.route_str+":delete:user:"+user_id})                       
            message.add_markup(markup_list)      
            
            reply_markup = request.message.json["message"]["reply_markup"]
            message.edit_message_text(request.message.from_user.id, 
                                        message_id=request.message.message.message_id, 
                                        new_text=mess_txt,
                                        reply_markup=reply_markup)                         
        elif request.is_script_command and command=="delete" and command_obj=="user":
            user_id = str(command_info)
            user = User(request.bot.conf_obj, user_id)
            username = user.get("username","")
            mess_txt = f"Наберите \"Yes\" для подтверждения удаления пользователя {username} c Id:{user.id}"    
            message.send(request.chatid, text=mess_txt)
            request.session.set({"del_user_waiting_for_input": user.id})
        elif hasattr(request.message, "text") and request.session.get("del_user_waiting_for_input", False)!=False:  
            user_id = request.session.get("del_user_waiting_for_input",0)  
            user = User(request.bot.conf_obj, user_id)  
            username = user.get("username","")  
            request.session.set({"del_user_waiting_for_input": False})
            mess_txt = f"Ошибка удаления пользователя {username} c Id:{user.id}"  
            if request.message.text.lower()=="yes":
                if user.delete_user():
                    mess_txt = f"Пользователь {username} c Id:{user.id} удален"
                    request.bot.reload_configs()
                else:
                    mess_txt = f"Ошибка удаления пользователя {username} c Id:{user.id}"      
            message.send(request.chatid, text=mess_txt)    
        else:   
            serv_user = User(request.bot.conf_obj, 0) 
            users_reestr = serv_user.get_users()
            for user_id, userdata in users_reestr.items():
                if not "params" in userdata or not type(userdata["params"]) is dict:
                    userdata["params"] = {}
                if not "roles" in userdata or not type(userdata["roles"]) is list:
                    userdata["roles"] = []       
                user_info = message.get_user_info(user_id)
                if not user_info is None:
                    userdata["params"] = {**userdata["params"], **user_info}           
                
                username = userdata.get("params", {}).get("username","")
                first_name = userdata.get("params", {}).get("first_name","")
                last_name = userdata.get("params", {}).get("last_name","")
                language_code = userdata.get("params", {}).get("language_code","")
                is_bot = userdata.get("params", {}).get("is_bot", False)

                mess_txt = "id: " + user_id
                if is_bot:
                    mess_txt += " (BOT)"
                mess_txt += " "+language_code+"\n"
                mess_txt += "username: " + username + "\n"   
                mess_txt += "first_name: " + first_name + "\n"
                if last_name!="":
                    mess_txt += "last_name: " + last_name + "\n"   
                mess_txt += "roles: " + ", ".join(userdata["roles"]) + "\n"

                markup_list = []
                for role in request.bot.config["system"]["allow_roles"]:
                    markup_list.append({"text":role, "command":request.route_str+":setrole:"+role+":"+str(user_id)})                      
                message.add_markup(markup_list)    
                message.add_markup([{"text":"Удалить", "command":request.route_str+":delete:user:"+str(user_id)}])      
                message.send(request.chatid, text=mess_txt)  


    def add_user(self, request:Request):
        logging.info(str(request.user.id)+": UserController:add_user")
        message = Message(request.bot.config["telegram"])
        
        if hasattr(request.message, "text") and request.session.get("add_user_waiting_for_input", False):
            request.session.set({"add_user_waiting_for_input": False})
            user_id = str(int(request.message.text))
            serv_user = User(request.bot.conf_obj, user_id)
            if serv_user.update_user():
                mess_txt = f"Пользователь {user_id} добавлен"
            else:
                mess_txt = f"Ошибка добавления пользователя {user_id}"  
            message.send(request.chatid, text=mess_txt)    
        else:
            mess_txt = "Введите идентификатор пользователя: "
            message.send(request.chatid, text=mess_txt)
            request.session.set({"add_user_waiting_for_input": True})
            




    