#!/usr/bin/python3
from agaunibot.botapp import BotApp
from agaunibot.lang import Lang

Lang.change_lang("en")

app = BotApp(BotApp.get_console_commands())
app.run()
