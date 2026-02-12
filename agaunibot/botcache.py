import redis
import logging
import json
import time

class BotCache:

    user = ""
    data = {}
    redis = None
    host = "localhost"
    port = 6379
    db = 0

    def __init__(self, *, user="", host="127.0.0.1", port=6379, db=0):
        if str(user) != "":
            self.user = str(user) + "::"
        self.host = host
        self.port = int(port)
        self.db = int(db)  
          
        self.connect()

    def connect(self):
        try:
            self.redis = redis.Redis(host=self.host, port=self.port, db=self.db)                    
            logging.info(f"Cache:connect: host {self.host} port {self.port} db {self.db}")
        except:
            logging.error(f"Cache:connect: host {self.host} port {self.port} db {self.db}")

    def check_connect(self):
        if self.redis is None:
            self.connect()
        try:
            self.redis.ping()    
            return True
        except:
            self.connect()
            try:
                self.redis.ping()    
                return True
            except:
                return False
                
    def get(self, key:str):
        if self.redis is None:
            return None
        cache_key = self.user + key    
        result = None
        try:
            res = self.redis.get(cache_key)
            if not res is None:
                result = json.loads(res)                
            else:
                result = res    
        except:
            self.check_connect()
            try:
                res = self.redis.get(cache_key)
                if not res is None:
                    result = json.loads(res)                
                else:
                    result = res                
            except:
                logging.error(f"Cache:get:key:{cache_key}")       
        return result
    
    def get_updtime(self, key:str):
        if self.redis == None:
            return None
        cache_key = self.user + key +"::updtime"    
        result = None
        try:
            res = self.redis.get(cache_key)
            if not res is None:
                result = json.loads(res)                
            else:
                result = res    
        except:
            self.check_connect()
            try:
                res = self.redis.get(cache_key)
                if not res is None:
                    result = json.loads(res)                
                else:
                    result = res                
            except:
                logging.error(f"Cache:get_updtime:key:{cache_key}")
        return result
    
    def rem(self, key:str):
        if self.redis == None:
            return False
        cache_key = self.user + key    
        try:
            self.redis.delete(cache_key)
            return True
        except:
            self.check_connect()
            try:
                self.redis.delete(cache_key)
                return True
            except:
                logging.error(f"Cache:rem:key:{cache_key}")
        return False

    def set(self, key:str, val, ex=None):
        if self.redis is None:
            return False
        cache_key = self.user + key    
        value = json.dumps(val)
        valtime = time.time()
        try:
            res = self.redis.set(cache_key, value)
            res = self.redis.set(cache_key+"::updtime", valtime)
            # print(cache_key, value)
            if not ex is None:
                self.redis.expire(cache_key, int(ex))
                self.redis.expire(cache_key+"::updtime", int(ex))
            return True    
        except:
            self.check_connect()
            try:
                res = self.redis.set(cache_key, value)
                res = self.redis.set(cache_key+"::updtime", valtime)
                if not ex is None:
                    self.redis.expire(cache_key, int(ex))
                    self.redis.expire(cache_key+"::updtime", int(ex))
                return True        
            except:
                logging.error(f"Cache:set:key:{cache_key}")
        return False
