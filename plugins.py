import pyrebase
import json
import configparser

config = configparser.ConfigParser()
config.read('cfg.ini', encoding="utf-8")



def cfg_cmd_clear(platform_str):
    clear_dict = {
            "Windows":"cls",
            "Linux":"clear"
        }
    return clear_dict[platform_str]