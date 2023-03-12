from exceptiongroup import ExceptionGroup, catch
import sqlite3
import streamlit as st
import pandas as pd
import os
import ast
import json


def load_file(file, folder):
    path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', folder, file ))
    with open(path) as f:
        data = f.read()
    if data:
        js = ast.literal_eval(data)
        return js
    else:
        print ("there is no data")
        return None

def write_file(data, name, ext, folder, overwrite):

    test = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config'))
    st.write(test)
    
    if ext:
        filename = name + "." + ext
    else:
        filename = name
    
    filepath = os.path.join(test, filename)


    #try:
    #    os.mkdir(os.path.join(here, folder))
    #except FileExistsError:
    #    pass



    json_object = json.dumps(data, indent = 4)
    with open(filepath, "w+") as outfile:
        outfile.seek(0)
        outfile.write(json_object)
        outfile.truncate()