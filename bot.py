#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# bot - telegram bot framework
# Copyright (C) 2024-2025 Konstantin Khachaturian - aga-c4@rambler.ru

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# В качестве лицензии можно юзать эти 2 строки:
# Copyright 2024-2025 Konstantin Khachaturian. GNU GPL3 license.
# GNU GPL3 license copy: https://www.gnu.org/licenses/gpl-3.0.txt
# First added by username: Konstantin Khachaturian
# Last updated by username: Konstantin Khachaturian



# pip3 install telebot, requests, logging, 

import sys
import argparse
import time
from datetime import datetime
import logging
import telebot 

from config import custom, defaultbot
from models.config import Config
from models.memsess import MemSess
from models.message import Message
from models.mybot import MyBot
from models.sysbf import SysBf
from models.user import User
from models.request import Request
from models.node import Node

start_time = time.time() 

# Обработка параметров
def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('action', nargs='?', type=str, default='')
    parser.add_argument ('--log_to', choices=['', 'console', 'file'], default='console')
    parser.add_argument ('--log_level', choices=['', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='WARNING')
    return parser 

# Обработка входных данных
parser = createParser()
namespace = parser.parse_args(sys.argv[1:])

logfile = 'log/umdom_bot' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.txt'
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

if namespace.log_to!='' and namespace.log_to=='file':       
    logging.basicConfig(level=log_level_val, filename=logfile, filemode='a')
    print(f"log_level: {log_level} logging FILE: ", logfile)  
else:
    logging.basicConfig(level=log_level_val)
    print(f"log_level: {log_level} to console")      

conf_obj = Config(custom=custom, 
                defaultbot=defaultbot, 
                allow_configs=["main", "botstru", "devices"]) 

if namespace.action == 'start':
    config = conf_obj.get_config("main")
    my_bot = MyBot(conf_obj)
    message = Message(config["telegram"])
    if message.get_status():
        message.send(config["telegram"]["channels"]["domchat"], text="Привет, Я включился!")

        tgbot = telebot.TeleBot(config["telegram"]["api_token"])

        @tgbot.message_handler(commands=['start'])
        def start(in_message):
            try:
                # Идентентификация пользователя
                user = User(conf_obj, in_message.from_user.id)

                # Маршрутизация
                if user.has_role("user"):    
                    route = my_bot.def_route
                    sess = MemSess(in_message.from_user.id)
                    sess.clear_session()
                    sess.set({"route": route})
                    sess.set({"pgnom": 0})
                else:
                    route = ["noauth"]
                    sess = None    

                request = Request(
                    bot = my_bot,
                    user = user, 
                    session = sess, 
                    route = route,
                    pgnom = 0,
                    message = in_message,
                    chatid = in_message.chat.id
                    )    

                # Открытие ноды
                node = Node(request)

                variants = node.get_variants(request)    
                message.add_markup(variants["variant_list"], "ReplyKeyboardMarkup")    
                message.send(in_message.chat.id, text="Привет, {name}! Я помогу с управлением домом".format(name=in_message.from_user.first_name))
                
                # Надо вызвать функцию ноды
                if node.get("contoller", False) and node.get("contoller_action", False):
                    node_model = SysBf.class_factory(config["bot"]["bot_controllers_prefix"]+node.get("contoller").lower(), node.get("contoller"))
                    logging.info("{0}: run {1}.{2}".format(user.id,node.get("contoller"),node.get("contoller_action")))
                    SysBf.call_method_fr_obj(node_model, node.get("contoller_action"), request)
            except:
                logging.warning("Error in message_handler:commands:start")     
                
        @tgbot.message_handler(content_types=['text'])
        def func(in_message):
            try:
                # Идентентификация пользователя
                user = User(conf_obj, in_message.from_user.id)

                # Маршрутизация
                same_route = False
                if user.has_role("user"):    
                    sess = MemSess(in_message.from_user.id)
                    route = sess.get("route", my_bot.def_route)
                    pgnom = sess.get("pgnom", 0)
                    btn_pg_prefix  = config["bot"]["btn_pg_prefix"]
                    btn_pg_prefix_len = len(btn_pg_prefix)
                    if in_message.text.startswith(btn_pg_prefix) and in_message.text[btn_pg_prefix_len:].isdigit():
                        pgnom = int(in_message.text[btn_pg_prefix_len:])
                        if pgnom>0:
                            pgnom -= 1   
                    else:
                        prev_route = str(route)
                        route = my_bot.get_route_by_variant(user, route, in_message.text)
                        sess.set({"route": route})
                        if str(route)!=prev_route:
                            pgnom = 0
                        elif route != my_bot.def_route:
                            same_route = True    
                    sess.set({"pgnom": pgnom})            
                else:
                    route = ["noauth"]
                    sess = None    
                    pgnom = 0

                request = Request(
                    bot = my_bot,
                    user = user, 
                    session = sess, 
                    route = route,
                    same_route = same_route,
                    pgnom = pgnom,
                    message = in_message,
                    chatid = in_message.chat.id
                    )              
                
                logging.info(f"{user.id}: route: {str(route)}  pgnom: {pgnom+1}")

                # Открытие ноды
                node = Node(request)

                if not same_route:
                    variants = node.get_variants(request)
                    request.set(node_variants=variants)
                    message.add_markup(variants["variant_list"], "ReplyKeyboardMarkup")    
                    if route!=my_bot.def_route:
                        message.add_markup([my_bot.main_variant, 
                                            variants["back_variant"],
                                            variants["forvard_variant"]], "ReplyKeyboardMarkup")
                    mess_txt = node.get("message", "").format(name=in_message.from_user.first_name)
                    message.send(in_message.chat.id, text=mess_txt)

                # Надо вызвать функцию ноды
                if node.get("contoller", False) and node.get("contoller_action", False):
                    node_model = SysBf.class_factory(config["bot"]["bot_controllers_prefix"]+node.get("contoller").lower(), node.get("contoller"))
                    logging.info("{0}: run {1}.{2}".format(user.id,node.get("contoller"),node.get("contoller_action")))
                    SysBf.call_method_fr_obj(node_model, node.get("contoller_action"), request)
            except:
                logging.warning("Error in message_handler:content_types:text")             

        @tgbot.callback_query_handler()
        def callback_query(in_message):
            try:
                # Идентентификация пользователя
                user = User(conf_obj, in_message.from_user.id)

                # Маршрутизация
                if user.has_role("user"):    
                    sess = MemSess(in_message.from_user.id)
                    prev_route = sess.get("route", my_bot.def_route)
                    pgnom = sess.get("pgnom", 0)
                    route = my_bot.get_route_by_str(user, in_message.data)
                    if route!=prev_route:
                        pgnom = 0
                        sess.set({"route": route})
                        sess.set({"pgnom": pgnom})   
                else:
                    route = ["noauth"]
                    sess = None    
                    pgnom = 0

                request = Request(
                    bot = my_bot,
                    user = user, 
                    session = sess, 
                    route = route,
                    pgnom = pgnom,
                    message = in_message,
                    chatid = in_message.from_user.id,
                    is_script_command = True
                    )              
                
                logging.info(f"{user.id}: route: {str(route)}  pgnom: {pgnom+1}")

                # Открытие ноды
                node = Node(request)

                spl = in_message.data.split(':')
                if len(spl)==1:
                    variants = node.get_variants(request)
                    request.set(node_variants=variants)
                    message.add_markup(variants["variant_list"], "ReplyKeyboardMarkup")    
                    if route!=my_bot.def_route:
                        message.add_markup([my_bot.main_variant, 
                                            variants["back_variant"],
                                            variants["forvard_variant"]], "ReplyKeyboardMarkup")
                    mess_txt = node.get("message", "")
                    message.send(in_message.from_user.id, text=mess_txt)

                # Надо вызвать функцию ноды
                if node.get("contoller", False) and node.get("contoller_action", False):
                    node_model = SysBf.class_factory(config["bot"]["bot_controllers_prefix"]+node.get("contoller").lower(), node.get("contoller"))
                    logging.info("{0}: run {1}.{2}".format(user.id,node.get("contoller"),node.get("contoller_action")))
                    SysBf.call_method_fr_obj(node_model, node.get("contoller_action"), request)
            except:
                logging.warning("Error in callback_query_handler")    

        @tgbot.message_handler(content_types=['document'])
        def handle_docs_photo(in_message):
            try:
                # Идентентификация пользователя
                user = User(conf_obj, in_message.from_user.id)

                # Маршрутизация
                if user.has_role("user"):    
                    sess = MemSess(in_message.from_user.id)
                    route = sess.get("route", my_bot.def_route)
                    pgnom = sess.get("pgnom", 0)
                else:
                    route = ["noauth"]
                    sess = None    
                    pgnom = 0

                request = Request(
                    bot = my_bot,
                    user = user, 
                    session = sess, 
                    route = route,
                    pgnom = pgnom,
                    message = in_message,
                    chatid = in_message.from_user.id,
                    is_script_command = True
                    )              
                
                logging.info(f"{user.id}: route: {str(route)}  pgnom: {pgnom+1}")

                # Открытие ноды
                node = Node(request)

                # Надо вызвать функцию ноды
                if node.get("contoller", False) and node.get("contoller_action", False):
                    node_model = SysBf.class_factory(config["bot"]["bot_controllers_prefix"]+node.get("contoller").lower(), node.get("contoller"))
                    logging.info("{0}: run {1}.{2}".format(user.id,node.get("contoller"),node.get("contoller_action")))
                    SysBf.call_method_fr_obj(node_model, node.get("contoller_action"), request)
            except:
                logging.warning("Error in message_handler:content_types:document")            

        while True:
            try:
                logging.info("Try to connect by Telebot")    
                tgbot.polling(none_stop=True)
            except:
                logging.warning("Error in Telebot, reconnect in 60s")    
                time.sleep(60)

    
else:
    print("""
#####################          
## bot
#####################
          
Synopsys:
    bot.sh [Command1] [Param1 Param_val1] [Param2 Param_val2] ...
        
Commands:
    start

Params:
    --log_level (DEBUG | INFO | WARNING | ERROR | CRITICAL) - run with log level (WARNING by default)  
    --log_to (console | file) - logs print to (console by default)          

Examples:
    bot.sh start --log_level INFO --log_to file
    bot.sh start                 
""")
    

print("----------------")    