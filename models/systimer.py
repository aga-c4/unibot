import time

class  SysTimer:

    start_ts = 0 # start Timestamp 

    def __init__(self):
        self.start_ts = time.time()

    def get_time(self):
        return round(time.time() - self.start_ts, 4)
