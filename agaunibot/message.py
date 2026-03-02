import logging
from time import sleep

from .sysbf import SysBf

class Message():
    status = True
    driver = None
    def_markup_row_width = 3

    @property
    def status(self):
        if self.import_driver is None or self.driver_class is None:
            return False
        return self.driver.get_status()

    def __init__(self, conf:dict):
        self.driver_alias = conf["messages"].get('driver_alias', None).lower()
        self.import_driver = conf["messages"].get('import_driver', None).lower()
        self.driver_class = conf["messages"].get('driver_class', None)
        self.def_markup_row_width = conf["messages"].get('def_markup_row_width', 3)
        if not self.import_driver is None and not self.driver_class is None:
            self.driver = SysBf.class_factory(self.import_driver, self.driver_class, conf.get(self.driver_alias, {}))
            logging.info("Use bot driver: {0}".format(self.driver_class)) 

    def bind_message_funct(self, botapp):
        self.driver.bind_message_funct(botapp)


    def send(self, channel:str, text:str, img_buf=None, reply_markup=None) -> int:
        if not self.status:
            return 0  

        res = 0
        logging.info(f"channel={channel}: Try to send: {text}")   
        try:
            if text!='':
                self.driver.send_message(channel, text, reply_markup=reply_markup) 
            res += 1
            if not img_buf is None:
                sleep(0.2)
                self.driver.send_photo(channel, img_buf)
        except Exception:
            logging.exception(f"channel=[{channel}]: Messages send error: {text}")

        return res
    
    def send_photo(self, channel:str, img_buf=None, reply_markup=None) -> int:
        if not self.status:
            return 0  
            
        res = None
        logging.info(f"channel={channel}: Try to send photo")   
        try:
            res = self.driver.send_photo(channel, img_buf=img_buf, reply_markup=reply_markup)
        except Exception:
            logging.exception(f"channel=[{channel}]: Photo send error")

        return res
    
    def send_document(self, channel:str, img_buf=None, reply_markup=None) -> int:
        if not self.status:
            return 0  

        res = None
        logging.info(f"channel={channel}: Try to send document")   
        try:
            res = self.driver.send_document(channel, document=img_buf, reply_markup=reply_markup)
        except Exception:
            logging.exception(f"channel=[{channel}]: Document send error")

        return res
    
    def download_file(self, message, filename:str):
        channel = 0
        if filename is None or filename.strip()=="":
            return None
        else:
            try:
                return self.driver.download_file(message.document.file_id, filename) 
            except:
                logging.exception(f"channel=[{channel}]: Error: Message:download_file")  
                return None     
    

    def edit_message_text(self, channel:str, message_id:str, *, new_text:str, reply_markup=None) -> int:
        if not self.status:
            return 0  

        logging.info(f"channel={channel}: message_id={message_id}: Try to edit: {new_text}")   
        try:
            if new_text!='':         
                self.driver.edit_message_text(channel=channel, 
                                           message_id=message_id, 
                                           new_text=new_text, 
                                           reply_markup=reply_markup)

                return 1
        except Exception:
            logging.exception(f"channel=[{channel}]: message_id={message_id}: Messages edit error: {new_text}")
            return 0
        
    def edit_message_media(self, channel:str, message_id:str, *, img_buf=None, reply_markup=None) -> int:
        if not self.status:
            return 0  

        logging.info(f"channel={channel}: message_id={message_id}: Try to edit: photo")   
        try:
            if not img_buf is None:       
                self.driver.edit_message_media(channel=channel, 
                                           message_id=message_id, 
                                           img_buf=img_buf,
                                           reply_markup=reply_markup)

                return 1
        except Exception:
            err_text = "" # TODO - вставить сюда сообщение об ошибке
            logging.exception(f"channel=[{channel}]: message_id={message_id}: Messages edit error: {err_text}")
            return 0    
        

    def delete_message_text(self, channel:str, message_id:str) -> int:
        if not self.status:
            return 0  

        logging.info(f"channel={channel}: message_id={message_id}: Try to delete")   
        try:
                self.driver.delete_message(channel=channel, message_id=message_id)
                return 1
        except Exception:
            logging.exception(f"channel=[{channel}]: message_id={message_id}: Messages delete error")
            return 0    
    

    def get_blank_markup_dict(self, *, mktype:str="InlineKeyboardMarkup", mklist:list=[], row_width:int=0):
        if row_width==0:
            row_width = self.def_markup_row_width
        if mktype=="ReplyKeyboardMarkup":
            mktype_str = "ReplyKeyboardMarkup"
        else:
            mktype_str = "InlineKeyboardMarkup"  
        if len(mklist)>0:      
            return {
                "type": mktype_str,
                "row_width": row_width,
                "items": mklist
            } 
        else:
            None       


    def get_user_info(self, user_id):
        try:
            return self.driver.get_user_info(user_id)
        except Exception as e:
            logging.warning(f"user_id={user_id}: get_chat error: {e}")
            return None
