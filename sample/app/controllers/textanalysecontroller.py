from agaunibot.user import User

class TextAnalyseController:   

    def analyse_text(self, params:dict={}):
        if not type(params) is dict:
            return None
        user = params.get("user", None) 
        bot = params.get("bot", None) 
        route = params.get("route", [])  
        text_to_analyse = params.get("text_to_analyse", "")   
        lang = params.get("lang", "")   

        if text_to_analyse!="тест":
            return None

        # cur_route = route[:]
        if user.auth:
            def_route = bot.def_route
        else:
            def_route = bot.def_route_noauth

        # if route is None:
        cur_route = def_route
        outtext = "А вот тут бот нафантазировал" 

        return {
            "route": cur_route,
            "same_route": False,
            "pgnom": 0,
            "command": "",
            "command_obj": "",
            "command_info": "",
            "text": outtext,
        }  
    
    
