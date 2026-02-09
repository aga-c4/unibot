import time
import random

from models.singleton import singleton

@singleton
class MemSess:

    session_timeout = 3600
    sessions = {}
    user_id_str = ''
    cleanup_iter_rand = 100

    def __init__(self, user_id, type:str="main", timeout:int=3600):
        current_time = time.time()
        self.user_id_str = str(user_id)
        self.type = type
        self.session_timeout = timeout
        if user_id!=0:  
            if not self.user_id_str in self.sessions:
                self.sessions[self.user_id_str] = {
                    "ts": current_time,
                    self.type: {}
                }    
            else:
                if not self.type in self.sessions[self.user_id_str]:
                    self.sessions[self.user_id_str]["ts"] = current_time
                    self.sessions[self.user_id_str][self.type] = {}


    def set(self, sess_vals:dict={}):
        if self.user_id_str!=0:
            current_time = time.time()
            self.sessions[self.user_id_str]["ts"] = current_time    
            self.sessions[self.user_id_str][self.type] = {**self.sessions[self.user_id_str][self.type], **sess_vals} # TODO - 2 уровень перезаписывает, не дополняет!
            if random.randint(1, self.cleanup_iter_rand)==1:
                self.cleanup_sessions()


    def get(self, key:str="", def_val=None):
        if key=="":
            return def_val
        if self.user_id_str==0:
            return None
        
        current_time = time.time()
        if current_time - self.sessions[self.user_id_str]["ts"] > self.session_timeout:
            self.sessions[self.user_id_str][self.type] = {}
            self.sessions[self.user_id_str]["ts"] = current_time
            return def_val
        
        self.sessions[self.user_id_str]["ts"] = current_time  
        if random.randint(1, 100)==1:
                self.cleanup_sessions()
        return self.sessions[self.user_id_str][self.type].get(key, def_val)
    

    def clear_session(self):
        if self.user_id_str!=0:
            current_time = time.time()
            self.sessions[self.user_id_str]["ts"] = current_time
            self.sessions[self.user_id_str][self.type] = {}


    def cleanup_sessions(self):
        current_time = time.time()
        for user_id, user_session in self.sessions.items():
            if current_time - user_session["ts"] > self.session_timeout:
                if user_id==self.user_id_str:
                    self.sessions[self.user_id_str][self.type] = {}
                    self.sessions[self.user_id_str]["ts"] = current_time
                else:    
                    del self.sessions[user_id]

    


