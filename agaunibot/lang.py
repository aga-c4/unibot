#!/usr/bin/python3
import gettext

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

class Lang:

    available_langs = []

    @staticmethod
    def set_available_langs(available_langs:list):
        Lang.available_langs = available_langs

    @staticmethod
    def change_lang(lang:str):
        if lang in Lang.available_langs:
            lang_ru = gettext.translation('messages', 'locale', languages=[lang])
            lang_ru.install()