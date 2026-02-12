import os
import logging
import json

from .sysbf import SysBf

class Config:

    defconfig = "default"
    custom = "default"
    allow_configs = ["main", "botstru", "devices"]
    use_def_configs = ["main", "botstru"]
    allow_save_configs = ["devices"]
    configs = {}

    def __init__(self, *, custom:str, defconfig:str="default", allow_configs:list=["main", "botstru"]):
        self.custom = custom
        self.defconfig = defconfig
        self.def_config_pref = f"app.configs.{defconfig}" # Путь к директории с конфигурациями по умолчанию
        self.def_config_dir = f"app/configs/{defconfig}" # Путь к директории с конфигурациями по умолчанию
        self.config_pref = f"app.configs.{self.custom}"  # Путь к директории с конфигурациями перекрывающими деф.
        self.config_dir = f"app/configs/{self.custom}"  # Путь к директории с конфигурациями перекрывающими деф.
        if type(allow_configs) is list:
             for conf_alias in allow_configs:
                 if not conf_alias in self.allow_configs:
                     self.allow_configs.append(conf_alias)
             allow_configs
        for conf_alias in allow_configs:
            self._load_config(conf_alias)       

    def save_config(self, config_data, config_type:str="main"):
        if self.config_dir==self.def_config_dir:
            return False
        config_file = config_type.lower()
        if config_file in self.allow_save_configs:
            user_conf_file = os.path.join(self.config_dir, config_file)+".json"
            try:
                with open(user_conf_file, 'w', encoding='utf-8') as file:   
                    json.dump(config_data, file, ensure_ascii=False, indent=4) 
                    return True
            except:    
                logging.warning("Error: Config:save_config")
                return False
        else:
            return False    
        
    def delete_config(self, config_type:str="main"):  
        if self.config_dir==self.def_config_dir:
            return False
        config_file = config_type.lower()
        user_conf_file = os.path.join(self.config_dir, config_file)+".json"  
        os.remove(user_conf_file)  
        logging.info("Delete user config {0}: {1}".format(config_type, user_conf_file))
        return True

    def _load_config(self, config_type, user_conf_file:str="nofile"):
        config_data = {}
        config_file = config_type.lower()
        config_def_module = self.def_config_pref+"."+config_file
        config_module = self.config_pref+"."+config_file
        config_def_path = os.path.join(self.def_config_dir, config_file)+".py"
        config_path = os.path.join(self.config_dir, config_file)+".py"
        user_conf_file = os.path.join(self.config_dir, config_file)+".json"

        cont = True
        if os.path.isfile(user_conf_file) and config_type in self.allow_configs:
            try:
                with open(user_conf_file, 'r', encoding='utf-8') as file:
                    logging.info("Load json config {0} from {1}".format(config_type, user_conf_file))
                    config_data = json.load(file)    
                    if not type(config_data) is dict:
                        config_data = {}
                    cont = False    
            except: 
                logging.warning("Error: Config:save_config")
            
        if cont:    
            if os.path.isfile(config_def_path) and config_type in self.use_def_configs:
                def_config_model = SysBf.class_factory(config_def_module, config_type)
                logging.info("Load def config {0} from {1}".format(config_type, config_def_path))
                config_data = getattr(def_config_model, "config", {})
            
            if config_path!=config_def_path and os.path.isfile(config_path):
                config_model = SysBf.class_factory(config_module, config_type)
                logging.info("Load config {0} from {1}".format(config_type, config_path))
                add_config_data = getattr(config_model, "config", {})
                # config_data = {**config_data, **add_config_data} # Рекурсивно не объединяет! Только на 1 уровне. update() работает аналогично
                config_data = SysBf.merge_dicts(config_data, add_config_data)
        self.configs[config_type] = config_data
        return True
    
    def clean_config_cache(self):
        logging.info("Clean config cache!")
        self.configs = {}


    def get_config(self, config_type:str="main"):
        if config_type not in self.configs:
            self._load_config(config_type)
        return self.configs[config_type]


    def get(self, conf_alias:str, key:str, defval=None):
        if conf_alias in self.configs:
            return self.configs[conf_alias].get(key, defval)
        else:
            return defval