from models.request import Request

class Node:

    route = []
    _data = {}

    def __init__(self, request:Request):
        self.route = request.route
        if request.user.no_roles:
            self._data = self.get_node_by_route(request, request.bot.def_route_noauth)
        else:        
            self._data = self.get_node_by_route(request)

    def get_node_by_route(self, request:Request, def_route:str=""):
        route = request.route
        if request.route is None or not type(request.route) is list:
            if def_route!="":
                route = def_route
            else:    
                route = request.bot.def_route   
        node = request.bot.bot_stru
        for key in route:   
            view_roles = node["variants"][key].get("access", {}).get("view", None)
            if "variants" in node and key in node["variants"] and \
                (view_roles is None or request.user.has_role(node["variants"][key].get("access", {}).get("view", None))):
                node = node["variants"][key]       
        return node 

    def get_variants(self, request:Request):
        result = {"variant_list": [], 
                  "forvard_variant":request.bot.dop_variant, 
                  "back_variant": request.bot.back_variant }
        if "variants" in self._data:
            items = 0
            variant_list = []
            forvard_found = False
            btn_in_pg = request.bot.config["bot"]["btn_in_pg"]
            btn_pg_prefix  = request.bot.config["bot"]["btn_pg_prefix"]
            for rt, variant in self._data["variants"].items():
                if request.user.has_role(variant.get("access", {}).get("view", None)):
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
        return self._data.get(key, defval)  
    
     