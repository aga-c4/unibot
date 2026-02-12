import logging

from .request import Request

class Node:

    route = []
    _data = {}


    def __init__(self, request:Request):
        self.route = request.route
        self._data = self.get_node_by_route(request)

    def get_node_by_route(self, request:Request, def_route:str=""):
        route = request.route
        if request.route is None or not type(request.route) is list:
            if def_route!="":
                route = def_route
            else:  
                if request.user.found_user:  
                    route = request.bot.def_route   
                else:
                    route = request.bot.def_route_noauth   
        node = request.bot.bot_stru
        node_exist = False
        for key in route:   
            view_roles = node["variants"][key].get("access", {}).get("view", None)
            if "variants" in node and key in node["variants"] and \
                (not type(view_roles) is dict
                 or request.user.has_role(node["variants"][key].get("access", {}).get("view", "noroles"))):
                node = node["variants"][key]    
                node_exist = True   
        if not node_exist:
            node = {}        
        return node 

    def get_variants(self, request:Request):
        result = {"variant_list": [], 
                  "forvard_variant":request.bot.dop_variant, 
                  "back_variant": request.bot.back_variant }
        if type(self._data) is dict and "variants" in self._data and type(self._data["variants"]) is dict:
            items = 0
            variant_list = []
            forvard_found = False
            btn_in_pg = request.bot.config["bot"]["btn_in_pg"]
            btn_pg_prefix  = request.bot.config["bot"]["btn_pg_prefix"]
            for rt, variant in self._data["variants"].items():
                variant_role = variant.get("access", {}).get("view", "noroles")
                if request.user.has_role(variant.get("access", {}).get("view", "noroles")):
                    if items>=request.pgnom*btn_in_pg and items<request.pgnom_next*btn_in_pg:
                        variant_list.append(variant["action"])
                    if not forvard_found and items>=request.pgnom_next*btn_in_pg:    
                        result["forvard_variant"] = f"{btn_pg_prefix}{request.pgnom_next+1}" 
                        forvard_found = True
                    items += 1    
            if request.pgnom>=1:
                result["back_variant"] = f"{btn_pg_prefix}{request.pgnom_prev + 1}"     
            result["variant_list"] = variant_list
        return result        
    
    def get(self, key:str, defval=None):
        if type(self._data) is dict:
            return self._data.get(key, defval)
        else:
            return defval  
    
     