import logging

from agaunibot.botapp import app
from agaunibot.request import Request
from app.models.demomodel import DemoModel

class DemoController:   

    def __init__(self):
        self.message = app.message 

    def get_info(self, request:Request):
        logging.info(str(request.user.id)+": DemoController:get_info")     
        demo_obj = DemoModel(request.bot)
        mess_txt = demo_obj.get_info()
        self.message.send(request.chatid, text=mess_txt) 

    def send_to_channel(self, request:Request):  
        chatid = request.bot.config["telegram"]["channels"]["domchat"]
        logging.info(str(request.user.id)+": DemoController:send_to_channel:"+str(chatid))    
        mess_txt = "Demo message to channel."
        self.message.send(chatid, text=mess_txt)     
    
    
