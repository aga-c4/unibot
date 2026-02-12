import logging

from agaunibot.mybot import MyBot
from agaunibot.request import Request
from agaunibot.message import Message

class DemoModel:

    bot = None
    data = {
        "mess_text": "Сообщения пользователей и другое.\n"
    }
    model = None
    access = {}
    out_path = "app/tmp/out"
    in_path = "app/tmp/in"
    commands = {}

    def __init__(self, bot:MyBot):
        self.bot = bot
        self.out_path = bot.config["system"].get("out_path", self.out_path)
        self.in_path = bot.config["system"].get("in_path", self.in_path)
    
    def get_info(self):
        logging.info("DemoModel:get_message")
        mess_txt = self.data["mess_text"]
        return mess_txt

    
    