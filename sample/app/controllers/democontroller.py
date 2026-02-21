import logging

from agaunibot.request import Request
from agaunibot.message import Message
from app.models.demomodel import DemoModel

class DemoController:   

    def get_info(self, request:Request):
        logging.info(str(request.user.id)+": DemoController:get_info")  
        message = Message(request.bot.config["telegram"])    
        demo_obj = DemoModel(request.bot)
        mess_txt = demo_obj.get_info()
        message.send(request.chatid, text=mess_txt) 

    def send_to_channel(self, request:Request):  
        chatid = request.bot.config["telegram"]["channels"]["domchat"]
        logging.info(str(request.user.id)+": DemoController:send_to_channel:"+str(chatid))  
        message = Message(request.bot.config["telegram"])    
        mess_txt = "Demo message to channel."
        message.send(chatid, text=mess_txt)     
    
    
