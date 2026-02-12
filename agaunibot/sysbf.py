import logging
import resource
from importlib import import_module

class SysBf:

    @staticmethod
    def get_max_memory_usage():
        max_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return max_memory

    @staticmethod
    def get_substring(text:str, start_text:str="", end_text:str=""):
        if start_text == "":
            start_index = 0
        else:
            start_index = text.find(start_text)   
        
        if end_text == "":
            end_index = len(text)
        else:
            end_index = text.find(end_text)

        if start_index == -1 or end_index == -1:
            return ""        
        
        return text[start_index + len(start_text):end_index]
    
    @staticmethod
    def class_factory(module_name, class_name, *args, **kwargs):
        logging.info(f"SysBF:Factory:New: {class_name} from {module_name}") 
        try:
            module = import_module(module_name)
            try:
                class_obj = getattr(module, class_name)
                try:
                    instance = class_obj(*args, **kwargs)
                    return instance  # Вы создали экземпляр класса.
                except:
                    logging.warning(f"Error new [{class_name}] in {class_obj.__class__.__name__}")        
            except:
                logging.warning(f"Error getattr [{class_name}]")        
        except:
            logging.warning(f"Error import_module [{module_name}]") 
        
        return None
    
    @staticmethod
    def call_method_fr_obj(obj, method_name, *args, **kwargs):
        # Получаем метод из объекта по имени
        method = getattr(obj, method_name, None)
        if callable(method):
            # Вызываем метод с переданными аргументами
            return method(*args, **kwargs)
        else:
            logging.warning(f"Method not found: {method_name} in {obj.__class__.__name__}")
            return None
            
    @staticmethod
    def merge_dicts(dict1, dict2):
        """Рекурсивно объединяет два словаря."""
        merged = dict1.copy()  # Копируем первый словарь

        for key, value in dict2.items():
            if key in merged:
                # Если значение - словарь, вызываем рекурсивно
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = SysBf.merge_dicts(merged[key], value)
                # Если значение - список, объединяем списки
                # elif isinstance(merged[key], list) and isinstance(value, list):
                #     merged[key] = list(set(merged[key]) | set(value))  # Объединяем списки без дубликатов
                else:
                    # В противном случае заменяем значение
                    merged[key] = value
            else:
                # Если ключа нет в первом словаре, просто добавляем его
                merged[key] = value

        return merged
    
    @staticmethod
    def merge_lists(list1, list2):
        """Рекурсивно объединяет два списка."""
        merged = list1.copy()  # Копируем первый список

        for item in list2:
            if item not in merged:  # Добавляем только уникальные элементы
                merged.append(item)

        return merged

    @staticmethod
    def getitem(source, item, default=None):
        if type(source) is list:
            item_int = int(item)
            if len(source)>item_int:
                return source[item_int]
        elif type(source) is dict:
            return source.get(item, default)     
        return default    
