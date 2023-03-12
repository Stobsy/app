import sqlite3
import streamlit as st
import pandas as pd
import os
import ast
import json
from util import db_util
from util import file_util
from util import auth
from io import StringIO
import os
import xml.etree.ElementTree as ET
import json
import ast
import numpy as np
import colorsys
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt 
from matplotlib.ticker import FormatStrFormatter
from scipy.optimize import least_squares
import altair as alt
from config import config
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from pandas.api.types import is_bool_dtype, is_numeric_dtype




name, authentication_status, username = auth.check()

if username != 'stobsy' and username != 'admin':
    st.error('This page is for admin users only')
else:
    config_file = config.load_config_file()
    #config_file['performance']['altitude_profile'] = list(np.linspace(5000, 45000, 9))




    globalVars = {
        "AL" : "4",
        "ozAltProfile" : np.linspace(5000, 45000, 9),
        "curvesToProcess" : ["ClimbTas","ClimbBurn","CruiseTas","CruiseBurn","ClimbRate"]
        #"curvesToProcess" : ["CruiseBurn"]
    }


    def create_database():
        st.header("Create Database")
        db_filename = st.text_input("DB Filename")
        create_db = st.button('Create Database')
        if create_db:
            if db_filename.endswith('.db'):
    
                try:
                    db_util.new_db(db_filename)
                    st.success("database created successfully") # success message?
                except Exception as e:
                    st.error("Error from main function")
                    e
            else: 
                st.error('DB filename must end with .db, please retry.')
            
   
                
    def db_view():
        st.header("Database Viewer")

        here = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'db'))
        sqlite_dbs = [file for file in os.listdir(here) if file.endswith('.db')]
        db_filename = st.selectbox('DB Filename', sqlite_dbs)
        
        con = db_util.con_db(db_filename)
        cur = con.cursor()


        st.subheader("aircraft")
        test = pd.read_sql("SELECT * FROM aircraft", con)
        test
        st.subheader("aircraft_types")
        test = pd.read_sql("SELECT * FROM aircraft_types", con)
        test
        st.subheader("perf_profiles")
        test = pd.read_sql("SELECT * FROM perf_profiles", con)
        test
        st.subheader("mission_profiles")
        test = pd.read_sql("SELECT * FROM mission_profiles", con)
        test
        st.subheader("perf_data")
        test = pd.read_sql("SELECT * FROM perf_data", con)
        test

        con.close()

        


    def run_query():
        st.header("Run Query")
      
        here = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'db'))
        databases = [file for file in os.listdir(here) if file.endswith('.db')]
        database = st.selectbox('Data Base in Use', databases)

        query = st.text_area("SQL Query", height=100)
        conn = db_util.con_db(database)
        submitted = st.button('Run Query')

        if submitted:
            try:
                query = conn.execute(query)
                cols = [column[0] for column in query.description]
                results_df= pd.DataFrame.from_records(
                    data = query.fetchall(), 
                    columns = cols
                )
                st.dataframe(results_df)
            except Exception as e:
                st.write(e)

        st.sidebar.markdown("# Run Query")

    def database_settings():

        st.header("Select Database")
        messages = st.container()
        here = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'db'))
        databases = [file for file in os.listdir(here) if file.endswith('.db')]
        messages = st.empty()
        if (config_file["database"] in databases):
            with st.form("database_settings_form"):
                index = databases.index(config_file["database"])
                database = st.selectbox('Select Database', databases, index = index)
                submitted = st.form_submit_button("Save Settings")
            if submitted:
                config_file["database"] = database
                config.save_config_file(config_file)
                messages.success("Database changed")
        else: 
            messages.error("Database not found - please select database to use")
            with st.form("database_settings_form"):
                database = st.selectbox('Select Database', databases)
                submitted = st.form_submit_button("Save Settings")
            if submitted:
                config_file["database"] = database
                messages.success("Database changed")
                config.save_config_file(config_file)

                    
            
                

    def submit_settings(database):
        config_file["database"] = database
        file_util.write_file(config_file, "config", "", "//config//", True)
            



                


    page_names_to_funcs = {
        "Select Database":database_settings,
        "Run Query": run_query,
        "Database Viewer": db_view,
        "Create Database": create_database,
    }

    selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
    page_names_to_funcs[selected_page]()
