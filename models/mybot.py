import logging
import requests
import json

from models.user import User
from models.config import Config

class MyBot:

    config = {}
    conf_obj = None
    bot_stru = {}
    locations = {}
    devices = {}
    def_route_noauth = ["noauth"]
    def_route = ["main"]
    main_variant = "Главная"
    forvard_variant = "Вперед"
    back_variant = "Назад"
    dop_variant = ""
    dop_variant_route = ["main"]


    def __init__(self, conf_obj:Config):
        self.custom = conf_obj.custom
        self.conf_obj = conf_obj
        self.config = conf_obj.get_config()
        self.bot_stru = conf_obj.get_config("botstru")
        self.locations = conf_obj.get_config("devices").get("locations", {})
        self.devices = conf_obj.get_config("devices").get("devices", {})
        if "def_route" in self.config["bot"]:
            self.def_route = self.config["bot"]["def_route"]   
        self.dop_variant = self.config["bot"]["nav_dop_variant"]
        self.dop_variant_route = self.config["bot"]["nav_dop_variant_route"]      

    def reload_configs(self):
        self.conf_obj.clean_config_cache()
        self.config = self.conf_obj.get_config()
        self.bot_stru = self.conf_obj.get_config("botstru")
        self.locations = self.conf_obj.get_config("devices").get("locations", {})
        self.devices = self.conf_obj.get_config("devices").get("devices", {})
        if "def_route" in self.config["bot"]:
            self.def_route = self.config["bot"]["def_route"]   
        print(self.locations)    
        logging.info("Bot reload configs")

    def get_node_by_route(self, route=None):
        if route is None or not type(route) is list:
            route = self.def_route   
        node = self.bot_stru
        for key in route:   
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
      
    def get_route_by_str(self, user:User, route_str:str=None): 
        cur_route = []
        route_str_upd = route_str.strip()
        if route_str_upd == "":
            return self.def_route
        all_route_list = route_str_upd.split(':')
        route_list = all_route_list[0].split('.')
        if len(route_list) == 0:
            route_list = self.def_route   
        
        node = self.get_node_by_route([])
        is_redirect = False
        for rt_item in route_list:   
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
        if len(cur_route) == 0:
            return self.def_route                
        return cur_route

    def get_route_by_variant(self, user:User, route=None, variant:str=""):
        cur_route = route[:]
        if route is None:
            cur_route = self.def_route[:]
        elif variant==self.main_variant:
            cur_route = self.def_route[:]
        elif variant==self.back_variant:
            if len(route)<2:
                prev_route = self.def_route[:]
            else:
                prev_route = route[:]
                del prev_route[-1]
            cur_route = prev_route  
        elif variant==self.dop_variant:
            cur_route = self.dop_variant_route    
        else:
            node = self.get_node_by_route(route)
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
        try:
            response = requests.get("https://api.ipify.org/?format=json")
            res = response.text
            if res:
                return json.loads(res).get("ip", "IP not found")     
            return "IP not found" 
        except:
            logging.info("Request api.ipify.org!")
            return "IP not found" 