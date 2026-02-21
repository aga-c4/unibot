import logging

from .user import User
from .config import Config

class MyBot:

    config = {}
    conf_obj = None
    bot_stru = {}
    locations = {}
    devices = {}
    def_route = ["def_node"]
    def_route_noauth = ["def_node_noauth"]
    main_variant = "Главная"
    forvard_variant = "Вперед"
    back_variant = "Назад"
    dop_variant = ""
    dop_variant_route = ["def_node"]
    dop_variant_noauth = ""
    dop_variant_route_noauth = ["def_node_noauth"]


    def __init__(self, conf_obj:Config):
        self.custom = conf_obj.custom
        self.conf_obj = conf_obj
        self.config = conf_obj.get_config()
        self.bot_stru = conf_obj.get_config("botstru")
        self.locations = conf_obj.get_config("devices").get("locations", {})
        self.devices = conf_obj.get_config("devices").get("devices", {})
        self.def_node = self.config["bot"]["def_node"]  
        self.def_node_noauth = self.config["bot"]["def_node_noauth"]
        self.def_route = self.config["bot"]["def_route"]  
        self.def_route_noauth = self.config["bot"]["def_route_noauth"]       
        self.main_variant = self.config["bot"]["main_variant"]    
        self.forvard_variant = self.config["bot"]["forvard_variant"]   
        self.back_variant = self.config["bot"]["back_variant"]   
        self.dop_variant = self.config["bot"]["nav_dop_variant"]
        self.dop_variant_route = self.config["bot"]["nav_dop_variant_route"]      
        self.dop_variant_noauth = self.config["bot"]["nav_dop_variant_noauth"]
        self.dop_variant_route_noauth = self.config["bot"]["nav_dop_variant_route_noauth"]      

    def reload_configs(self):
        self.conf_obj.clean_config_cache()
        self.config = self.conf_obj.get_config()
        self.bot_stru = self.conf_obj.get_config("botstru")
        self.locations = self.conf_obj.get_config("devices").get("locations", {})
        self.devices = self.conf_obj.get_config("devices").get("devices", {})
        if "def_route" in self.config["bot"]:
            self.def_route = self.config["bot"]["def_route"]  
        if "def_route_noauth" in self.config["bot"]:
            self.def_route_noauth = self.config["bot"]["def_route_noauth"]            
        print(self.locations)    
        logging.info("Bot reload configs")

    def get_node_by_route(self, route=None, lang:str="", def_route:list=None):
        ''' Возвращает элемент массива ноды по route (list), def_route - маршрут по умолчанию без языка '''
        if route is None or not type(route) is list:
            route = def_route   
        node = self.bot_stru
        lang_sf = ""
        if lang!="":
            lang_sf = "_" + lang
        for key in route:   
            if key=="def_node_noauth":
                key = self.def_node_noauth + lang_sf 
            if key=="def_node":
                key = self.def_node + lang_sf
            if "variants" in node and key in node["variants"]:
                node = node["variants"][key]       
        return node 
    
    def get_dev_comm_by_str(self, route_str:str=None): 
        command = ""
        obj = ""
        info = ""
        route_str_upd = route_str.strip()
        if route_str_upd != "":
            all_route_list = route_str_upd.split(':')
            if len(all_route_list)>1:
                command = all_route_list[1].strip()
            if len(all_route_list)>2:
                obj = all_route_list[2].strip()
            if len(all_route_list)>3:
                info = all_route_list[3]    

        return (command, obj, info)
    
    def get_controller_route_by_str(self, route_str:str=None): 
        result = []
        if route_str != "":
            all_route_list = route_str.split(':')
            if len(all_route_list)>1:
                result = all_route_list[1:]    
        return result
    
    def set_lang_to_route(self, *, route:list=[], lang:str=""): 
        '''Вернет маршут с примененным языком'''

        lang_sf = ""
        if lang!="":
            lang_sf = "_" + lang
        result=[]    
        for rt_item in route:   
            if rt_item=="def_node_noauth":
                rt_item = self.def_node_noauth + lang_sf 
            if rt_item=="def_node":
                rt_item = self.def_node + lang_sf
            result.append(rt_item)
        return result     
    

    def get_route_by_str(self, *, user:User, route_str:str="", lang:str=""): 
        '''Вернет маршут с примененным языком'''
        
        if user.auth:
            def_route = self.def_route[:]   
        else:
            def_route = self.def_route_noauth[:]
        cur_route = self.set_lang_to_route(route=def_route, lang=lang)    
        route_str_upd = route_str.strip()
        if route_str_upd == "":
            return cur_route

        all_route_list = route_str_upd.split(':')
        route_list = all_route_list[0].split('.')
        if len(route_list) == 0:
            route_list = def_route

        node = self.get_node_by_route(lang=lang, def_route=def_route)
        is_redirect = False
        lang_sf = ""
        if lang!="":
            lang_sf = "_" + lang
        for rt_item in route_list:   
            if rt_item=="def_node_noauth":
                rt_item = self.def_node_noauth + lang_sf 
            if rt_item=="def_node":
                rt_item = self.def_node + lang_sf
            if "variants" in node:
                for var_rt, var_node in node["variants"].items():
                    if var_rt==rt_item:
                        if 'redirect' in var_node and type(var_node['redirect']) is list:
                            cur_route = var_node['redirect']
                            logging.info(str(user.id)+": redirect_to: " + str(cur_route))
                            is_redirect = True
                        else:       
                            cur_route.append(var_rt)
                        node = var_node
                        break    
            if is_redirect:
                break                                 
                
        return cur_route

    def get_route_by_variant(self, *, user:User, route:list=None, variant:str="", lang:str=""):
        '''Вернет маршут с примененным языком'''
        cur_route = route[:]
        if user.auth:
            def_route = self.set_lang_to_route(route=self.def_route, lang=lang)
        else:
            def_route = self.set_lang_to_route(route=self.def_route_noauth, lang=lang)

        if route is None:
            cur_route = def_route
        elif variant==self.main_variant:
            cur_route = def_route
        elif variant==self.back_variant:
            if len(route)<2:
                prev_route = def_route[:]
            else:
                prev_route = route[:]
                del prev_route[-1]
            cur_route = self.set_lang_to_route(route=prev_route, lang=lang)  
        elif user.auth and variant==_(self.dop_variant):
            cur_route = self.set_lang_to_route(route=self.dop_variant_route, lang=lang)    
        elif variant==_(self.dop_variant_noauth):
            cur_route = self.set_lang_to_route(route=self.dop_variant_route_noauth, lang=lang)        
        else:
            node = self.get_node_by_route(lang=lang, def_route=def_route)
            if "variants" in node:  
                for var_rt, var_node in node["variants"].items():
                    if "action" in var_node and var_node["action"]==variant:
                        if 'redirect' in var_node and type(var_node['redirect']) is list:
                            cur_route = var_node['redirect']
                            logging.info(str(user.id)+": redirect_to: " + str(cur_route))
                        else:       
                            cur_route.append(var_rt)
                        break           
        return cur_route
     
    def get_ip(self):
        return "IP not found" 
    
    def get_data_from_message(self, in_message, route_data:dict=None):
        res = {
            "command": "",
            "command_obj": None,
            "command_info": None,
            "text": ""
        }
        if not route_data is None and type(route_data) is dict:
            res["command"] = route_data.get("command", ""),
            res["command_obj"] =  route_data.get("command_obj", ""),
            res["command_info"] = res["redirect"].get("command_info", ""),
            res["text"] = res["redirect"].get("text", "")
        else:
            if hasattr(in_message, "data"):
                command, command_obj, command_info = self.get_dev_comm_by_str(in_message.data)
                res["command"] = command
                res["command_obj"] = command_obj
                res["command_info"] = command_info
            if hasattr(in_message, "text"):
                res["text"] = in_message.text  
        return res    