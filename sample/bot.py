#!/usr/bin/python3
import gettext

from agaunibot.botapp import BotApp

# To generate lang files run commands:
# 
# 1. Generate .pot
# sudo apt install gettext
# xgettext -d messages -o locale/ru/LC_MESSAGES/messages.pot bot.py
# 
# 2. Generate .po
# msginit -l es_ES.UTF8 -o locale/ru/LC_MESSAGES/messages.po -i locale/ru/LC_MESSAGES/messages.pot --no-translator
# 
# 3. Generate .mo
# msgfmt -c locale/ru/LC_MESSAGES/messages.po -o locale/ru/LC_MESSAGES/messages.mo

def change_lang(lang:str):
    if lang=="ru":
        lang_ru = gettext.translation('messages', 'locale', languages=['ru'])
        lang_ru.install()
    elif lang=="en":
        lang_en = gettext.translation('messages', 'locale', languages=['en'])
        lang_en.install() 
change_lang("en")

app = BotApp(BotApp.get_console_commands())
app.run()
