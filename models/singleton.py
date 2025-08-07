class _SingletonWrapper:

    def __init__(self, cls):
        """Класс-обeртка для реализации паттерна Singleton"""
        self.__wrapped__ = cls  # Оригинальный класс
        self._instance = None   # Экземпляр класса
        
    def __call__(self, *args, **kwargs):
        """Возвращает единственный экземпляр класса"""
        if self._instance is None:
            self._instance = self.__wrapped__(*args, **kwargs)
        return self._instance    

def singleton(cls):
    """Декоратор для класса, реализующий синглтон"""
    return _SingletonWrapper(cls)    