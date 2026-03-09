'''
Фасад для работы с базами данных, реализует паттерн мультисинглтон, когда
в параметр создания объекта передается алиас настройки, а обратно возвращается
ссылка на объект для работы с базой, описанной в заданной настройке. 
Для каждой настройки создается только одна база. Таким образом мы можем 
одновременно использовать разные базы с разными драйверами, пользуясь при этом
всеми преимуществами синглтона. Если не задано, то дефолтная настройка - "default"
'''

import logging
from .sysbf import SysBf
from typing import Final

class DB:

    config = {}
    db_obj = {}

    def use_config(self, config:dict={}):
        self.config = config

    def get_obj(self, dbalias='default'): 
        # if dbalias in self.db_obj:
        #     return self.db_obj[dbalias]
        # el
        if dbalias in self.config:
            self.config[dbalias]["import_driver"] 
            db_model = SysBf.class_factory(self.config[dbalias]["import_driver"], 
                                           self.config[dbalias]["driver_class"],
                                           **self.config[dbalias]["init_params"])
            if db_model is not None:
                logging.info("DB: use DB {1} from {0}".format(self.config[dbalias]["import_driver"], 
                                                    self.config[dbalias]["driver_class"]))
                db_model.connect()
                # self.db_obj[dbalias] = db_model
                return db_model
            else:
                logging.warning("DB: No DB class {1} from {0}".format(self.config[dbalias]["import_driver"], 
                                                    self.config[dbalias]["driver_class"]))
                return None
        else:
            return None

db_manager:Final[DB] = DB()