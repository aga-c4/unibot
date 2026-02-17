import telebot
from telebot import types # для указание типов
from telebot.util import quick_markup
import logging
from time import sleep
import json

from .singleton import singleton

@singleton
class Message():
    status = True
    bot = None
    parse_mode = 'HTML'
    markup = None
    markup_type = None

    def __init__(self, telegram_conf:dict):
        self.status = True
        telegram_conf = telegram_conf
        
        if self.status:
            telegram_api_token = telegram_conf.get('api_token', None)
            if telegram_api_token is None:
                self.status = False
            
        if self.status:
            try:    
                self.bot = telebot.TeleBot(telegram_api_token)
            except:
                logging.warning("TeleBot init problems!")
                self.status = False

    def get_status(self):
        return self.status

    def send(self, channel:str, *, text:str, img_buf=None) -> int:
        if not self.status:
            return 0  

        res = 0
        logging.info(f"channel={channel}: Try to send: {text}")   
        try:
            if text!='':
                self.bot.send_message(channel, text, disable_web_page_preview=True, parse_mode=self.parse_mode, reply_markup=self.markup)
            res += 1
            if not img_buf is None:
                sleep(0.2)
                self.bot.send_photo(channel, img_buf)
        except:
            logging.warning(f"channel=[{channel}]: Messages send error: {text}")

        self.clean_markup()
        return res
    
    def send_photo(self, channel:str, *, img_buf=None) -> int:
        if not self.status:
            return 0  

        res = None
        logging.info(f"channel={channel}: Try to send photo")   
        try:
            res = self.bot.send_photo(channel, img_buf, reply_markup=self.markup)
        except:
            logging.warning(f"channel=[{channel}]: Photo send error")

        self.clean_markup()
        return res
    
    def send_document(self, channel:str, *, img_buf=None) -> int:
        if not self.status:
            return 0  

        res = None
        logging.info(f"channel={channel}: Try to send document")   
        try:
            res = self.bot.send_document(channel, document=img_buf, reply_markup=self.markup)
        except:
            logging.warning(f"channel=[{channel}]: Document send error")

        self.clean_markup()
        return res
    
    def download_file(self, message, filename:str):
        channel = 0
        if filename is None or filename.strip()=="":
            return None
        else:
            try:
                file_info = self.bot.get_file(message.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)
                with open(filename, 'wb') as new_file:
                    new_file.write(downloaded_file)
                return filename    
            except:
                logging.warning(f"channel=[{channel}]: Error: Message:download_file")  
                return None     
    

    def edit_message_text(self, channel:str, message_id:str, *, new_text:str, reply_markup=None) -> int:
        if not self.status:
            return 0  

        logging.info(f"channel={channel}: message_id={message_id}: Try to edit: {new_text}")   
        try:
            if new_text!='':
                use_markup = None
                if not reply_markup is None and type(reply_markup) is dict and "inline_keyboard" in reply_markup:
                    markup = types.InlineKeyboardMarkup(row_width=3)
                    for mkitemlist in reply_markup["inline_keyboard"]:
                        add_list = []
                        for mkitem in mkitemlist:
                            add_list.append(types.InlineKeyboardButton(mkitem["text"], callback_data=mkitem["callback_data"]))
                        if len(add_list)>0:
                            markup.add(*add_list)  
                            use_markup = markup     

                self.bot.edit_message_text(chat_id=channel, 
                                           message_id=message_id, 
                                           text=new_text, 
                                           reply_markup=use_markup)
                self.clean_markup()
                return 1
        except:
            logging.warning(f"channel=[{channel}]: message_id={message_id}: Messages edit error: {new_text}")
            return 0
        
    def edit_message_media(self, channel:str, message_id:str, *, img_buf=None, reply_markup=None) -> int:
        if not self.status:
            return 0  

        logging.info(f"channel={channel}: message_id={message_id}: Try to edit: photo")   
        try:
            if not img_buf is None:
                use_markup = None
                if not reply_markup is None and type(reply_markup) is dict and "inline_keyboard" in reply_markup:
                    markup = types.InlineKeyboardMarkup(row_width=3)
                    for mkitemlist in reply_markup["inline_keyboard"]:
                        add_list = []
                        for mkitem in mkitemlist:
                            add_list.append(types.InlineKeyboardButton(mkitem["text"], callback_data=mkitem["callback_data"]))
                        if len(add_list)>0:
                            markup.add(*add_list)  
                            use_markup = markup     

                photo = types.InputMediaPhoto(img_buf)
                self.bot.edit_message_media(chat_id=channel, 
                                           message_id=message_id, 
                                           media=photo, 
                                           reply_markup=use_markup)
                self.clean_markup()
                return 1
        except:
            err_text = "" # TODO - вставить сюда сообщение об ошибке
            logging.warning(f"channel=[{channel}]: message_id={message_id}: Messages edit error: {err_text}")
            return 0    
        

    def delete_message_text(self, channel:str, message_id:str) -> int:
        if not self.status:
            return 0  

        logging.info(f"channel={channel}: message_id={message_id}: Try to delete")   
        try:
                self.bot.delete_message(chat_id=channel, message_id=message_id)
                self.clean_markup()
                return 1
        except:
            logging.warning(f"channel=[{channel}]: message_id={message_id}: Messages delete error")
            return 0    
        

    def add_markup(self, mklist=[], mktype:str="InlineKeyboardMarkup"):
        if not type(mklist)==list:
            return False
        if len(mklist)==0:
            return False
        if mktype=="InlineKeyboardMarkup" and (self.markup_type is None or self.markup_type==mktype):
            if self.markup is None:    
                self.markup = types.InlineKeyboardMarkup(row_width=3)
                self.markup_type=mktype
            add_list = []
            for mkitem in mklist:
                if type(mkitem) is dict:
                    add_list.append(types.InlineKeyboardButton(mkitem["text"], callback_data=mkitem["command"]))
                else:
                    add_list.append(types.InlineKeyboardButton(mkitem, callback_data=mkitem))    
            self.markup.add(*add_list)    
        elif mktype=="ReplyKeyboardMarkup" and (self.markup_type is None or self.markup_type==mktype):    
            if self.markup is None:    
                self.markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                self.markup_type=mktype
            self.markup.add(*mklist)    
        return True


    def clean_markup(self):
        self.markup = None
        self.markup_type = None


    def get_user_info(self, user_id):
        try:
            user = self.bot.get_chat(user_id)  # Получаем информацию о пользователе
            user_info = {
                'first_name': user.first_name
            }
            if type(user.username) is str:
                user_info["username"] = user.username
            else:
                user_info["username"] = ""    
            return user_info
        except Exception as e:
            logging.warning(f"user_id={user_id}: get_chat error: {e}")
            return None
