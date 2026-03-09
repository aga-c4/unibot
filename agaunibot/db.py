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

<<<<<<< HEAD
    def get_obj(self, dbalias='default'): 
        # if dbalias in self.db_obj:
        #     return self.db_obj[dbalias]
        # el
        if dbalias in self.config:
=======
    def get_obj(self, dbalias='default'):
        if dbalias in self.db_obj:
            return self.db_obj[dbalias]
        elif dbalias in self.config:
>>>>>>> 59a609ad112685e061cc79571f37a88ba7ce3899
            self.config[dbalias]["import_driver"] 
            db_model = SysBf.class_factory(self.config[dbalias]["import_driver"], 
                                           self.config[dbalias]["driver_class"],
                                           **self.config[dbalias]["init_params"])
            if db_model is not None:
<<<<<<< HEAD
                logging.info("DB: use DB {1} from {0}".format(self.config[dbalias]["import_driver"], 
                                                    self.config[dbalias]["driver_class"]))
                db_model.connect()
                # self.db_obj[dbalias] = db_model
                return db_model
            else:
                logging.warning("DB: No DB class {1} from {0}".format(self.config[dbalias]["import_driver"], 
                                                    self.config[dbalias]["driver_class"]))
=======
                logging.info("{0}: use DB {2} from {1}".format(self.config[dbalias]["import_driver"], 
                                                    self.config[dbalias]["driver_class"]))
                # db_model.connect()
                self.db_obj[dbalias] = db_model
                return self.db_obj[dbalias]
            else:
>>>>>>> 59a609ad112685e061cc79571f37a88ba7ce3899
                return None
        else:
            return None

<<<<<<< HEAD
db_manager:Final[DB] = DB()
=======
db:Final[DB] = DB()
>>>>>>> 59a609ad112685e061cc79571f37a88ba7ce3899
