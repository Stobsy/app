from util import file_util
import os
import json
import streamlit as st
from datetime import date, time, datetime
import shutil



def load_config_file():
    folder = os.path.dirname(os.path.realpath(__file__))
    config_file = file_util.load_file("config", folder + "\\")
    return config_file


def save_config_file(file):
    #filepath = os.path.join(test, filename)
    path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '', "config"))
    backup = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '', "backup config "+ str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))))
    check = shutil.copy(path,backup)
    json_object = json.dumps(file, indent = 4)
    with open(path, "w") as outfile:
        outfile.write(json_object)
