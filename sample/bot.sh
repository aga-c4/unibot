#!/bin/bash

# Укажите полный путь к рабочей папке
# cd /home/...
# PYTHONPATH="/home/..."

# Получаем параметры, с которыми запущен bash скрипт
params="$@"

# Запускаем python3 скрипт с полученными параметрами
source ./venv/bin/activate
python3 bot.py $params
