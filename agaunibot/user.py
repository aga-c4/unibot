import os
import json
import logging

from .config import Config
from .message import Message

class User:

    config_obj = None
    users_file_path = ""
    found_user = False
    is_root = False
    _data = {
            "id": "0",
            "params": {},
            "roles": []
            }
    
    def __init__(self, config_obj:Config, user_id:int=0):
        self.config_obj = config_obj
        user_id_str = str(user_id)
        custom = self.config_obj.custom.lower()
        self._data["id"] = user_id_str
        if user_id_str in self.config_obj.get_config()["system"]["telegram_admin_ids"]:
            self.is_root = True
            self.found_user = True
        self.users_file_path = f"app/configs/{custom}/users.json"
        users_reestr = self.get_users()          
        if user_id_str in users_reestr:
            self.found_user = True   
            self._data["params"] = users_reestr[user_id_str].get("params", {})
            self._data["roles"] = users_reestr[user_id_str].get("roles", [])    
    
    @property
    def id(self):
        return self._data["id"]
    
    @property
    def roles(self):
        return self._data["roles"]
    
    def no_roles(self):
        if len(self._data["roles"])==0:
            return True
        else:
            return False
        
    def get_roles(self):
        if self.is_root:
            return ["admin"]
        return self._data.get("roles", [])

    def has_role(self, role, mode:str=""):
        """mode='all' - отключение авто True для admin""" 
        if self.is_root \
            or (not role is None and role=="noroles") \
            or (mode!="all" and "admin" in self._data["roles"]) \
            or (not role is None and role in self._data["roles"]): 
            return True
        else:
            return False
        
    def add_role(self, roles):
        if type(roles) is list:
            roles_in = roles        
        else:    
            roles_in = [roles]        
        if not self.found_user:
            return False
        if self.is_root:
            return False

        roles = self._data.get("roles",[])
        upd_ok = False
        for role in roles_in: 
            role = role.lower()
            if not role in roles and role.lower() in self.config_obj.get_config()["system"]["allow_roles"]:
                roles.append(role)
                self._data["roles"] = roles
                upd_ok = True
        if upd_ok:        
            return self.update_user()  
        return False

    def del_role(self, roles):
        if type(roles) is list:
            roles_in = roles        
        else:    
            roles_in = [roles]        
        if not self.found_user:
            return False
        if self.is_root:
            return False

        roles = self._data.get("roles",[])
        upd_ok = False
        for role in roles_in: 
            role = role.lower()
            if role in roles:
                roles.remove(role)
                self._data["roles"] = roles
                upd_ok = True
        if upd_ok:        
            return self.update_user()  
        return False     

    def update_user(self):
        user_id = str(self._data.get("id", 0))
        if self.users_file_path == "":
            return False
        if self.is_root:
            return False
        if user_id==0:
            return False

        if not "params" in self._data or not type(self._data["params"]) is dict:
            self._data["params"] = {}
        if not "roles" in self._data or not type(self._data["roles"]) is list:
            self._data["roles"] = []       
        message = Message(self.config_obj.get_config()["telegram"])
        user_info = message.get_user_info(user_id)
        if not user_info is None and type(user_info) is dict:
            for item, itemval in user_info.items():
                if item in ["is_bot", "language_code", "username", "first_name", "last_name"]:
                    self._data["params"][item] = itemval      

        users_reestr = {}
        try:
            with open(self.users_file_path, 'r', encoding='utf-8') as file:
                users_reestr = json.load(file)    
                if not type(users_reestr) is dict:
                    users_reestr = {}

            users_reestr[user_id] = self._data         

            with open(self.users_file_path, 'w', encoding='utf-8') as file:   
                json.dump(users_reestr, file, ensure_ascii=False, indent=4)     
                return True
        except:
            logging.warning("Error: User:update_user:file")

        return False 

    def delete_user(self):
        user_id = str(self._data.get("id", 0))
        if self.users_file_path == "":
            return False
        if self.is_root:
            return False
        if user_id==0:
            return False

        try:
            users_reestr = {}
            with open(self.users_file_path, 'r', encoding='utf-8') as file:
                users_reestr = json.load(file)    
                if not type(users_reestr) is dict:
                    users_reestr = {}

            if user_id in users_reestr:
                del(users_reestr[user_id])

            with open(self.users_file_path, 'w', encoding='utf-8') as file:   
                json.dump(users_reestr, file, ensure_ascii=False, indent=4)  
                return True
        except:
            logging.warning("Error: User:delete_user:file")

        return False     


    def get_users(self):
        logging.info(str(self.id)+": get users from path:" + self.users_file_path)
        users_reestr = {}
        try:
            if os.path.isfile(self.users_file_path):
                with open(self.users_file_path, 'r', encoding='utf-8') as file:
                    users_reestr = json.load(file)    
                    if not type(users_reestr) is dict:
                        users_reestr = {}
            else:
                logging.warning(self.id+": Error: Not found users_file_path, create:" + self.users_file_path) 
                with open(self.users_file_path, 'w', encoding='utf-8') as file:   
                    json.dump({}, file, ensure_ascii=False, indent=4)       
                users_reestr = {}           
        except:
            logging.warning("Error: User:get_users:file")    

        return users_reestr                     


    def set(self, **kwargs):
        if type(kwargs)==dict:
            self._data["params"] = {**self._data["params"], **kwargs} 

    def get(self, key:str, defval=None):
        return self._data["params"].get(key, defval)    

    @property
    def id(self):
        return self._data.get("id", 0)   

    @property
    def data(self):
        return self._data 
