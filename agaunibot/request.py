class Request:

    _data = {        
            "bot": None,
            "session": None,
            "route": [],
            "pgnom": 0,
            "user": None,
            "message": None,
            "chatid": None,
            "is_script_command": False
        }

    def __init__(self, **kwargs):
        """Request(bot=bot, session=session, route=route, user=user, message=message)"""
        if type(kwargs)==dict:
            self._data = {**self._data, **kwargs} 
            if "pgnom" in kwargs:
                pgnom = int(kwargs["pgnom"])
                if pgnom<1:
                    pgnom_prev = 0
                else:
                    pgnom_prev = pgnom - 1 
                self._data["pgnom"] = pgnom
                self._data["pgnom_prev"] = pgnom_prev
                self._data["pgnom_next"] = pgnom + 1 

    @property
    def bot(self):
        return self._data.get("bot", {})
    
    @property
    def user(self):
        return self._data.get("user", 0)    

    @property
    def session(self):
        return self._data.get("session", None) 

    @property
    def route(self):
        return self._data.get("route", None) 
    
    @property
    def route_str(self):
        return '.'.join (self._data.get("route", []))
    
    @property
    def same_route(self):
        return self._data.get("same_route", False) 
    
    @property
    def pgnom(self):
        return self._data.get("pgnom", 0) 
    
    @property
    def pgnom_prev(self):
        return self._data.get("pgnom_prev", 0) 
    
    @property
    def pgnom_next(self):
        return self._data.get("pgnom_next", 0) 

    @property
    def message(self):
        return self._data.get("message", None)    
    
    @property
    def chatid(self):
        return self._data.get("chatid", None)    
    
    @property
    def is_script_command(self):
        return self._data.get("is_script_command", False)    

    def set(self, **kwargs):
        """set(bot=bot, session=session, route=route, user=user, message=message...)"""
        if type(kwargs)==dict:
            self._data = {**self._data, **kwargs} 
            if "pgnom" in kwargs:
                pgnom = int(kwargs["pgnom"])
                if pgnom<1:
                    pgnom_prev = 0
                else:
                    pgnom_prev = pgnom - 1 
                self._data["pgnom"] = pgnom
                self._data["pgnom_prev"] = pgnom_prev
                self._data["pgnom_next"] = pgnom + 1 

    def get(self, key:str, defval=None):
        return self._data.get(key, defval)
        
          