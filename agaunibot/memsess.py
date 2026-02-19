import time
import random

from .user import User

class MemSess:

    session_timeout = 3600
    sessions = {}
    cleanup_iter_rand = 100

    @property
    def exist(self):
        return self.user_id_str in MemSess.sessions and self.type in MemSess.sessions[self.user_id_str]
    

    def __init__(self, user:User, type:str="main"):
        self.type = type
        self.user_id = int(user.id)
        self.user_id_str = str(user.id)
        if self.user_id_str in MemSess.sessions:
            self.up()
            user.set_auth(self.get("user_auth"), False) 

    @staticmethod
    def set_timeout(timeout:int=3600):
        MemSess.timeout = timeout    


    def up(self):
        current_time = time.time()
        if self.user_id_str in MemSess.sessions and current_time - MemSess.sessions[self.user_id_str]["ts"] > self.session_timeout:
            self.delete()
            return
        elif not self.user_id_str in MemSess.sessions:
            MemSess.sessions[self.user_id_str] = {
                "start_ts": current_time,
                self.type: {}
            }
        elif not self.type in MemSess.sessions[self.user_id_str]:
            MemSess.sessions[self.user_id_str][self.type] = {}                           
        MemSess.sessions[self.user_id_str]["ts"] = current_time
        MemSess.sessions[self.user_id_str]["fin_ts"] = current_time + MemSess.timeout
            

    def set(self, sess_vals:dict={}):
        if self.user_id_str in MemSess.sessions:
            if not self.type in MemSess.sessions[self.user_id_str]:
                MemSess.sessions[self.user_id_str][self.type] = {} 
            # TODO - 2 уровень перезаписывает, не дополняет!
            MemSess.sessions[self.user_id_str][self.type] = {**MemSess.sessions[self.user_id_str][self.type], **sess_vals} 
            if random.randint(1, self.cleanup_iter_rand)==1:
                self.cleanup()


    def get(self, key:str="", def_val=None):
        if not self.exist or key=="":
            return def_val 
        if random.randint(1, 1000)==1:
                self.cleanup()
        return MemSess.sessions[self.user_id_str][self.type].get(key, def_val)
    

    def clear(self):
        if self.user_id_str in MemSess.sessions:
            MemSess.sessions[self.user_id_str][self.type] = {}

    def delete(self):
        if self.user_id_str in MemSess.sessions:
            del MemSess.sessions[self.user_id_str]        

    def cleanup(self):
        current_time = time.time()
        for user_id, user_session in MemSess.sessions.items():
            if current_time > user_session["fin_ts"] and user_id!=self.user_id_str:
                del MemSess.sessions[user_id]

    


