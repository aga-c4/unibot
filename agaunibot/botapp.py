import sys
import argparse
import time
from datetime import datetime
import logging
from typing import Final

from .config import Config
from agaunibot.lang import Lang
from .memsess import MemSess
from .message import Message
from .mybot import MyBot
from .sysbf import SysBf
from .user import User
from .request import Request
from .node import Node
from .db import db_manager

class BotApp:

    _data = {}

    def run(self, params:dict={}): 
        self.params = params
        BotApp.set_logsConfig(self.params) 
        defconfig = params.get("defconfig", "default")
        custom = params.get("custom", "default")
        self.start_time = time.time() 
        self.config = Config(custom=custom, 
                  defconfig=defconfig, 
                  allow_configs=["main", "botstru", "devices"]) 
        config = self.config.get_config("main") 
        self.available_langs = config["system"].get("available_langs", "ru")
        if type(self.available_langs) is list:
            Lang.set_available_langs(self.available_langs)
        self.default_lang = config["system"].get("default_lang", "ru")    
        if type(self.default_lang) is str and self.default_lang in Lang.available_langs:
            Lang.install_lang(self.default_lang)
        self.bot = MyBot(self.config)
        self.message = Message(config)
        self.request = None
        db_manager.use_config(config=config.get("db", {}))
        self.db = db_manager

        # TODO - Продумать уведомления
        # if self.message.status:
        #     self.message.send(config["telegram"]["channels"]["domchat"], text=f"Bot started!") 


        action = self.params.get("action", "")       
        custom = self.params.get("custom", "")    
        print(f"Try to run bot with custom {custom}")  

        if action == 'start':
            if self.message.status:
                self.message.bind_message_funct(self)
        elif action == 'debug':
            pass        
        else:
            BotApp.help()

    @staticmethod
    def help():   
        print("""
#####################          
## bot
#####################
          
Synopsys:
    bot.sh [Command] [Param1 Param_val1] [Param2 Param_val2] ...

bot:          
    running bot alias from bots
           
Commands:
    start

Params:
    --custom - custom config alias (by default custom=default)      
    --log_level (DEBUG | INFO | WARNING | ERROR | CRITICAL) - run with log level (WARNING by default)  
    --log_to (console | file) - logs print to (console by default)          

Examples:
    bot.sh start --log_level INFO --log_to file
    bot.sh start --custom demo --log_level DEBUG
    bot.sh start --custom demo 
    bot.sh start                             
""")

    
    def set(self, **kwargs):
        """set(bot=bot, config=config, message=message...)"""
        if type(kwargs)==dict:
            self._data = {**self._data, **kwargs} 

    def get(self, key:str, defval=None):
        return self._data.get(key, defval)

    def use_route(self, in_message, message_type:str="text", route_data:dict=None):
        config = self.config.get_config("main")     
        # Идентентификация пользователя
        user = User(self.config, in_message.from_user["id"])
        sess = MemSess(user)
        lang = sess.get("lang", self.default_lang)
        _ = Lang.get_lang_funct(lang)
        pgnom = 0
        same_route = False
        def_route = self.bot.set_lang_to_route(route=self.bot.def_route, lang=lang)
        def_route_noauth = self.bot.set_lang_to_route(route=self.bot.def_route_noauth, lang=lang)
        text_to_analyse = ""

        # Маршрутизация
        if not route_data is None and type(route_data) is dict:
            route_str = ".".join(route_data.get("route", []))
            route = self.bot.get_route_by_str(user=user, route_str=route_str, lang=lang)
            same_route = route_data.get("same_route", False)
            pgnom = route_data.get("pgnom", 0)
            message_type = route_data.get("message_type", "text")
        elif message_type=="start":
            if user.auth: 
                route = def_route
                sess.clear()
            else:    
                route = def_route_noauth  
        else:
            if user.auth:    
                route = self.bot.set_lang_to_route(route=sess.get("route", def_route), lang=lang)   
            else:    
                route = def_route_noauth
            btn_pg_prefix  = config["bot"]["btn_pg_prefix"]
            btn_pg_prefix_len = len(btn_pg_prefix)
            if message_type=="text" and in_message.text.startswith(btn_pg_prefix) and in_message.text[btn_pg_prefix_len:].isdigit():
                pgnom = int(in_message.text[btn_pg_prefix_len:])
                if pgnom>0:
                    pgnom -= 1   
                    # Отработала команда, номер страницы сменился, почистим текст, чтоб дальше не мешался
                    in_message.text = ""      
            else:
                prev_route = str(route)  
                if message_type=="callback":
                    route = self.bot.get_route_by_str(user=user, route_str=in_message.data, lang=lang)  
                elif message_type=="text": 
                    old_route = route[:]  
                    route = self.bot.get_route_by_variant(user=user, route=route, variant=in_message.text, lang=lang)    
                    # Отработала команда, роут сменился, почистим текст, чтоб дальше не мешался
                    if old_route!=route:
                        in_message.text = ""    
                    else:    
                        text_to_analyse = in_message.text
                if str(route)!=prev_route:
                    pgnom = 0
                elif str(route) != str(def_route) and str(route) != str(def_route_noauth):
                    same_route = True       

        if message_type=="callback" or message_type=="document":
            chatid = in_message.from_user["id"]
            is_script_command = True
        else:
            chatid = in_message.chat["id"]
            is_script_command = False      

        # Анализа введенного текста, если будет найдено соответствие, то будет выведен текст
        # и/или пользователь будет перекинут на заданный маршрут
        if text_to_analyse!="":
            analyse_text_controller = config["bot"].get("analyse_text_controller", None)
            if not analyse_text_controller is None:
                analyse_text_model = SysBf.class_factory(config["bot"]["bot_controllers_prefix"]+analyse_text_controller.lower(), analyse_text_controller)
                logging.info("{0}: run {1}.{2}".format(user.id,analyse_text_controller,"analyse_text"))
                route_data = SysBf.call_method_fr_obj(analyse_text_model, "analyse_text", {
                            "user":user, 
                            "bot": self.bot,
                            "session": sess,
                            "message": in_message,
                            "chatid": chatid,
                            "route":route, 
                            "text_to_analyse":text_to_analyse, 
                            "lang":lang}) 
            if not route_data is None:
                logging.info(f"{user.id}: analyse_text success result!")
                route_str = ".".join(route_data.get("route", []))
                route = self.bot.get_route_by_str(user=user, route_str=route_str, lang=lang)
                same_route = route_data.get("same_route", False)
                pgnom = route_data.get("pgnom", 0)
                message_type = route_data.get("message_type", "text")

        request = Request(
            bot = self.bot,
            user = user, 
            session = sess,
            lang = lang, 
            route = route,
            same_route = same_route,
            pgnom = pgnom,
            message = in_message,
            message_type = message_type, 
            route_data = route_data,
            chatid = chatid,
            is_script_command = is_script_command
            )   
        self.request = request    

        logging.info(f"{user.id}: route={str(route)}; pgnom={pgnom+1}; same_route={same_route}; message_type={message_type}; lang={lang}")
        logging.info(f"{user.id}: auth={user.auth}; roles={user.roles}")
        if in_message.command!="":
            logging.info(f"{user.id}: is_script_command={is_script_command}; command={in_message.command}; command_obj: {in_message.command_obj}; command_info={in_message.command_info}")

        # Открытие ноды
        node = Node(request)
        if user.auth and not node.get("fast_back", False):
            sess.set({"route": route})
            sess.set({"pgnom": pgnom})    

        if_auth_redirect = node.get("if_auth_redirect", None)
        if user.auth and type(if_auth_redirect) is list:
            route = self.bot.set_lang_to_route(route=if_auth_redirect, lang=lang)
            same_route = False
            pgnom = 0
            message_type = "text"
            route_data = None
            is_script_command = False   
            request = Request(
                bot = self.bot,
                user = user, 
                session = sess,
                lang = lang, 
                route = route,
                same_route = same_route,
                pgnom = pgnom,
                message = in_message,
                message_type = message_type, 
                route_data = route_data,
                chatid = chatid,
                is_script_command = is_script_command
                )  
            self.request = request
            node = Node(request)  
            if not node.get("fast_back", False):
                sess.set({"route": route})
                sess.set({"pgnom": pgnom}) 


        # Вывод кнопок основной навигации и сообщения роута
        if message_type=="callback":
            spl = in_message.data.split(':')
            if len(spl)==1:
                variants = node.get_variants(request)
                request.set(node_variants=variants)
                mklist = []
                if len(variants["variant_list"])>0:
                    mklist.append(variants["variant_list"])  
                if str(route)!=str(def_route) and not node.get("fast_back", False):
                    markup_variants = [self.bot.main_variant, variants["back_variant"]]
                    if variants["forvard_variant"]:
                        markup_variants.append(variants["forvard_variant"])
                    mklist.append(markup_variants)
                mess_txt = node.get("message", "")
                markup = self.message.get_blank_markup_dict(mklist=mklist, mktype="ReplyKeyboardMarkup")   
                self.message.send(in_message.from_user["id"], text=mess_txt, reply_markup=markup)    

        elif message_type!="document"  and not same_route:
            variants = node.get_variants(request)
            request.set(node_variants=variants)
            mklist = []
            if len(variants["variant_list"])>0:
                mklist.append(variants["variant_list"])  
            if route!=str(def_route) and str(route)!=str(def_route_noauth) \
                and not node.get("fast_back", False):
                markup_variants = [self.bot.main_variant, variants["back_variant"]]
                if variants["forvard_variant"]:
                    markup_variants.append(variants["forvard_variant"])
                mklist.append(markup_variants)
            if type(route_data) is dict and route_data.get("text", "")!="":
                mess_txt = route_data.get("text", "")
            else:    
                mess_txt = node.get("message", "").format(name=in_message.from_user["first_name"]) 
            markup = self.message.get_blank_markup_dict(mklist=mklist, mktype="ReplyKeyboardMarkup")      
            self.message.send(in_message.chat["id"], text=mess_txt, reply_markup=markup)

        # Надо вызвать функцию ноды
        if node.get("contoller", False) and node.get("contoller_action", False):
            node_model = SysBf.class_factory(config["bot"]["bot_controllers_prefix"]+node.get("contoller").lower(), node.get("contoller"))
            logging.info("{0}: run {1}.{2}".format(user.id,node.get("contoller"),node.get("contoller_action")))
            res = SysBf.call_method_fr_obj(node_model, node.get("contoller_action"), request) 
            # По результату работы контроллера возможен редирект
            if type(res) is dict and "redirect" in res and type(res["redirect"]) is dict: 
                message_type = res["redirect"].get("message_type", "text")
                if user.auth:    
                    route = sess.get("route", self.bot.def_route)
                    pgnom = sess.get("pgnom", 0)
                else:    
                    route = self.bot.def_route_noauth
                    pgnom = 0
                route_data = {
                    "route": res["redirect"].get("route", route),
                    "same_route": res["redirect"].get("same_route", False),
                    "pgnom": res["redirect"].get("pgnom", 0),
                    "command": res["redirect"].get("command", ""),
                    "command_obj": res["redirect"].get("command_obj", ""),
                    "command_info": res["redirect"].get("command_info", ""),
                    "text": res["redirect"].get("text", ""),
                }
                self.use_route(in_message=in_message, message_type=message_type, route_data=route_data)


    @staticmethod
    def createParser ():
        # Обработка параметров
        parser = argparse.ArgumentParser()
        parser.add_argument ('action', nargs='?', type=str, default='')
        parser.add_argument ('--custom', type=str, default='')
        parser.add_argument ('--log_to', choices=['', 'console', 'file'], default='console')
        parser.add_argument ('--log_level', choices=['', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='WARNING')
        return parser 

    @staticmethod
    def get_console_commands():
        # Обработка входных данных
        parser = BotApp.createParser()
        namespace = parser.parse_args(sys.argv[1:])

        # Базовая конфигурация бота, переопределяемая кастомной конфигурацией
        defconfig = "default"
        custom = "default"
        if namespace.custom!='':
            custom = namespace.custom    

        # Настройки логирования
        log_level = "WARNING"
        log_level_val = logging.WARNING
        if namespace.log_level!='':
            if namespace.log_level=='DEBUG':
                log_level = namespace.log_level
                log_level_val = logging.DEBUG
            elif namespace.log_level=='INFO':       
                log_level = namespace.log_level
                log_level_val = logging.INFO
            elif namespace.log_level=="WARNING":      
                log_level = namespace.log_level
                log_level_val = logging.WARNING
            elif namespace.log_level=='ERROR':       
                log_level = namespace.log_level 
                log_level_val = logging.ERROR
            elif namespace.log_level=='CRITICAL':       
                log_level = namespace.log_level
                log_level_val = logging.CRITICAL
        
        log_to = "stdout"
        if namespace.log_to!='' and namespace.log_to=='file':       
            log_to = "file"

        logfile = f"logs/bot" + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.txt'        

        return{
            "defconfig": defconfig,
            "custom": custom,
            "action": namespace.action,
            "log_to": log_to, 
            "log_level": log_level,
            "log_level_val": log_level_val,
            "logfile": logfile
        }

    @staticmethod
    def set_logsConfig(params:dict={}):
        log_level_val = params.get("log_level_val", logging.WARNING)
        log_level = params.get("log_level", "WARNING")
        logfile = params.get("logfile", "")
        log_to = params.get("log_to", "")
        if log_to=='file' and logfile!="":       
            logging.basicConfig(level=log_level_val, filename=logfile, filemode='a')
            print(f"log_level: {log_level} logging FILE: ", logfile)  
        else:
            logging.basicConfig(level=log_level_val)
            print(f"log_level: {log_level} to console")            


app:Final[BotApp] = BotApp()