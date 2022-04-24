import json
from random import shuffle, randint
import logging
from time import sleep, time
import requests

from Config import Config
from utils.Language import Language
from utils.UserReader import UserReader
from utils.UAGetter import UAGetter
from utils.AESCipher import AESCipher

logging.basicConfig(format='[%(levelname)s] %(asctime)s: %(message)s', level=logging.INFO)

class Clockin:
    _user_json = None
    _clockin_url = None
    _clockin_method = None
    _clockin_data = None
    _clockin_header = None
    
    def __init__(self, user_json) -> None:
        self._user_json = user_json
        logging.info(Language().get_message('clockin_start') + '-' + self._user_json['remarks'] + '-' + self._user_json['id'])
        
    def clockin(self) -> bool:
        if self._clockin_method == 'POST':
            logging.info(Language().get_message('clockin_data') + '-' + str(self._clockin_data))
            try:
                response = requests.post(self._clockin_url, data=self._clockin_data, headers=self._clockin_header)
            except requests.ConnectionError:
                logging.error(Language().get_message('error_connection'))
                return False
            except requests.HTTPError:
                logging.error(Language().get_message('error_http'))
                return False
            except TimeoutError:
                logging.error(Language().get_message('error_timeout'))
                return False
            except:
                logging.error(Language().get_message('error_unknown'))
                return False
            if response.status_code == 200:
                logging.info(Language().get_message('clockin_success') + '-' + self._user_json['remarks'] + '-' + self._user_json['id'])
                logging.info(Language().get_message('clockin_response') + '-' + response.text)
                return True
            else:
                logging.warning(Language().get_message('clockin_fail') + '-' + self._user_json['remarks'] + '-' + self._user_json['id'])
                logging.warning(Language().get_message('clockin_response') + '-' + response.text)
                return False
        elif self._clockin_method == 'GET':
            logging.error(Language().get_message('request_method_not_support'))
            return False
        else:
            logging.error(Language().get_message('request_method_not_support'))
            return False
    
    def _generate_data(self) -> None:
        pass
    pass

class ShixiClockin(Clockin):    
    _name_longitude = None
    _name_latitude = None
    _name_temperature = None
    _name_verify = None
    
    def __init__(self, user_json) -> None:
        super().__init__(user_json)
        self._clockin_url = Config().get_config_str('clockinapi', 'shixi_qian_url')
        self._clockin_method = Config().get_config_str('clockinapi', 'shixi_qian_method')
        self._clockin_data = Config().get_config_json('clockinapi', 'shixi_qian_data')
        self._clockin_header = Config().get_config_json('clockinapi', 'shixi_qian_header')
        self._clockin_header['User-Agent'] = UAGetter().get_random_ua()
        
        self._name_temperature = Config().get_config_str('clockinapi', 'shixi_qian_temperature_field_name')
        self._name_longitude = Config().get_config_str('clockinapi', 'shixi_qian_longitude_field_name')
        self._name_latitude = Config().get_config_str('clockinapi', 'shixi_qian_latitude_field_name')
        self._name_verify = Config().get_config_str('clockinapi', 'shixi_qian_verify_field_name')
        
    def _generate_data(self) -> None:
        self._clockin_data[self._name_temperature] = '36.' + str(randint(1, 9))
        location = self.get_position_from_address_by_baidumap(self._user_json['address'])
        self._clockin_data[self._name_longitude] = location['lng']
        self._clockin_data[self._name_latitude] = location['lat']
        self._encrypt_verify()
        
    def _encrypt_verify(self) -> None:
        cipher = AESCipher(Config().get_config_str('shixiencrypt', 'shixi_qian_AES_KEY'), Config().get_config_str('shixiencrypt', 'shixi_qian_AES_IV'))
        self._clockin_data[self._name_verify] = cipher.encrypt(str(int(time())) + ',' + self._user_json['phone'])
        
    def get_position_from_address_by_baidumap(self, address) -> dict:
        try:
            return json.loads(requests.get(Config().get_config_str('baidumap', 'geocoding_url').format(address=address)).text)['result']['location']
        except:
            logging.error(Language().get_message('error_baidumap') + '-' + address)
            return {'lng': '', 'lat': ''}
    
    def clockin(self) -> bool:
        self._generate_data()
        if super().clockin():
            return True
        else:
            return False


class ClockinClockin(Clockin):
    _name_id = None
    _name_temperature = None
    _name_province = None
    _name_city = None
    _name_district = None
    _name_address = None
    
    def __init__(self, user_json) -> None:
        super().__init__(user_json)
        self._clockin_url = Config().get_config_str('clockinapi', 'clockin_url')
        self._clockin_method = Config().get_config_str('clockinapi', 'clockin_method')
        self._clockin_data = Config().get_config_json('clockinapi', 'clockin_data')
        self._clockin_header = Config().get_config_json('clockinapi', 'clockin_header')
        self._clockin_header['User-Agent'] = UAGetter().get_random_ua()
        
        self._name_id = Config().get_config_str('clockinapi', 'clockin_id_field_name')
        self._name_temperature = Config().get_config_str('clockinapi', 'clockin_temperature_field_name')
        self._name_province = Config().get_config_str('clockinapi', 'clockin_province_field_name')
        self._name_city = Config().get_config_str('clockinapi', 'clockin_city_field_name')
        self._name_district = Config().get_config_str('clockinapi', 'clockin_district_field_name')
        self._name_address = Config().get_config_str('clockinapi', 'clockin_address_field_name')
        
    def _generate_data(self) -> None:
        self._clockin_data[self._name_temperature] = '36.' + str(randint(1, 9))
        self._clockin_data[self._name_id] = self._user_json['id']
        self._clockin_data[self._name_province] = self._user_json['province']
        self._clockin_data[self._name_city] = self._user_json['city']
        self._clockin_data[self._name_district] = self._user_json['district']
        self._clockin_data[self._name_address] = self._user_json['address']
        
    def clockin(self) -> bool:
        self._generate_data()
        if super().clockin():
            return True
        else:
            return False
    

if __name__ == '__main__':
    logging.info(Language().get_message('name') + '-' + Config().get_config_str('app', 'name'))
    logging.info(Language().get_message('author') + '-' + Config().get_config_str('app', 'author'))
    logging.info(Language().get_message('version') + '-' + Config().get_config_str('app', 'version'))
    
    user_list = UserReader().get_user_list()
    if len(user_list) > 1:
        user_list = shuffle(user_list)
    
    for user in user_list:
        ShixiClockin(user).clockin()
        ClockinClockin(user).clockin()
        sleep(randint(1, 3))
