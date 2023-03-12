from exceptiongroup import ExceptionGroup, catch
import sqlite3
import streamlit as st
import pandas as pd
import os
import ast
import json

def new_db(name):
    folder = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'db'))
    excs = []
    try:
        st.write(name)
        con = con_db(name)
    except Exception as e:
        st.error("here")
        raise
    cur = con.cursor()
    try:
        cur.execute("CREATE TABLE perf_data_raw(name, data)")
        con.commit()
    except Exception as e:
        excs.append(e)
    #con.execute("DROP TABLE perf_data_sets")
    try:
        cur.execute("CREATE TABLE perf_data_points(data)")
        con.commit()
    except Exception as e:
        excs.append(e)
    
    

    try:
        cur.execute("CREATE TABLE perf_profiles(name, weight, curve, ozrwy_prof)")
        con.commit()
    except Exception as e:
        excs.append(e)
    try:
        data = [
            ("Learjet 3x Clean",None, None, None),
            ("Learjet 60 Clean",None, None, None),
            ("Learjet 31 Clean",None, None, None),
            ("Learjet 3x Pod",None, None, None),
            ("Kingair B200 Clean",None, None, None)
        ]
        cur.executemany("INSERT INTO perf_profiles VALUES(?, ?, ?, ?)", data)
        con.commit()
    except Exception as e:
        excs.append(e)



    try:
        cur.execute("CREATE TABLE aircraft_types (name, perf_profile, perf_weight)")
        con.commit()
    except Exception as e:
        excs.append(e)
    try:
        data = [
            ("Learjet 35 Normal Tip Tank",0,17000),
            ("Learjet 35 Normal Extended Tip Tank",0,17000),
            ("Learjet 36 Normal Tip Tank",0,17000),
            ("Learjet 35 Extended Tip Tank",0,17000),
            ("Learjet 31",2,15500),
            ("Learjet 31 ER",2,15500),
            ("Learjet 60",1,21000),
            ("KingAir B200",4,5000)
        ]
        cur.executemany("INSERT INTO aircraft_types VALUES(?, ?, ?)", data)
        con.commit()
    except Exception as e:
        excs.append(e)



    try:
        cur.execute("CREATE TABLE perf_data(ID, Weight, Altitude, CruiseTas, CruiseBurn, ClimbTas, ClimbBurn, ClimbRate, TAT, SAT)")
        con.commit()
    except Exception as e:
        excs.append(e)

    try:
        cur.execute("CREATE TABLE mission_profiles(name, desig)")
        con.commit()
    except Exception as e:
        excs.append(e)
    try:
        data = [
            ("Civilian", "CIV"),
            ("Military", "CIV"),
            ("Target Tow", "MTR"),
            ("Fire Scan", "FSC"),
            ("Aero-Med", "AMD"),
        ]
        cur.executemany("INSERT INTO mission_profiles VALUES(?, ?)", data)
        con.commit()
    except Exception as e:
        excs.append(e)

    try:
        cur.execute("CREATE TABLE aircraft(ID)")
        con.commit()
    except Exception as e:
        excs.append(e)


    try:
        cur.execute("CREATE TABLE kml_projects (name, description, notes, user, data, shapes)")
        con.commit()
    except Exception as e:
        excs.append(e)

    if excs:
        con.close()
        raise ExceptionGroup("Test Failures", excs)


    
    return
    
    

def con_db(name):
    folder = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'db'))

    con = None
    path = folder + "\\" + name
    try:
   
        con = sqlite3.connect(path)
    except Exception as e:
        raise
    return con