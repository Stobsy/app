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
import streamlit as st
import pandas as pd

globalVars = {
    "AL" : "4",
    "ozAltProfile" : np.linspace(5000, 45000, 9),
    "curvesToProcess" : ["ClimbTas","ClimbBurn","CruiseTas","CruiseBurn","ClimbRate"]
    #"curvesToProcess" : ["CruiseBurn"]
}

#CIV   MIL   MTR   FSC   AMD
profiles_matrix = np.array([
[None, None, 3   , 3   , None], #Learjet 35 Normal Tip Tank
[None, None, 3   , 3   , None], #Learjet 35 Normal Extended Tip Tank
[None, None, 3   , 3   , None], #Learjet 36 Normal Tip Tank
[None, None, 3   , 3   , None], #Learjet 35 Extended Tip Tank
[None, None, None, None, None], #Learjet 31
[None, None, None, None, None], #Learjet 31 ER
[None, None, None, None, None], #Learjet 60
[None, None, None, None, None]  #KingAir B2NoneNone
])


def load_file(file):
    here = os.path.dirname(os.path.realpath(__file__))

    path = here + "\\" + file

    with open(path) as f:
        data = f.read()
    if data:
        js = ast.literal_eval(data)
        return js
    else:
        print ("there is no data")
        return None

def write_file(data, name, ext, subdir):
    here = os.path.dirname(os.path.realpath(__file__))
    filename = name + "." + ext
    filepath = os.path.join(here, subdir, filename)
    try:
        os.mkdir(os.path.join(here, subdir))
    except FileExistsError:
        pass



    json_object = json.dumps(data, indent = 4)
    with open(filepath, "w+") as outfile:
        outfile.seek(0)
        outfile.write(json_object)
        outfile.truncate()




def curveFit(x , y, poly):
    xn = np.linspace(min(x), max(x), 50)
    popt = np.polyfit(x, y, poly)
    yn = np.polyval(popt, xn)
    return (xn , yn, popt)

def createPerf(profiles_perf):
    for aircraftProfile in profiles_perf:
        data = aircraftProfile["data"]
        
        #aircraftWeight = aircraftLib[type]["ozweight"]
        wts = list(dict.fromkeys([row["Weight"] for row in data])) #get list of unique weights
        
        wtsInt = list(map(int, wts))
        #closestWt = min(wtsInt, key=lambda x:abs(x-int(aircraftWeight)))
        #closestCurve = ""
        wts.sort()
        
        
        curves = {}
        for i , wt in enumerate(wts):
            curves[wt]={}
            
            for parameter in globalVars["curvesToProcess"]:   
                dataPoints = list(filter(lambda item: item['Weight'] == wt, data))
                x = []
                y = []
                for dataPoint in dataPoints:
                    if dataPoint[parameter] != "0" and dataPoint["Altitude"] != "0":
                        x.append(dataPoint["Altitude"])
                        y.append(dataPoint[parameter])
                        #convert list of str to integers
                        x = [int(numeric_string) for numeric_string in x]
                        y = [int(numeric_string) for numeric_string in y]
                        #check there is somthing in x and y
                        if x and y:
                            #fit the curve
                            xFit, yFit, curve = curveFit(x,y,3)
                            curves[wt][parameter]=curve

        
        aircraftProfile["ozRwy"] = {}
        for i , wt in enumerate(wts):
            if wt:


                aircraftProfile["ozRwy"][wt] = []
                for alt in globalVars["ozAltProfile"]:
                    #get a parameter template for each altitude
                    perf = dict(template_perf)
                    for parameter in globalVars["curvesToProcess"]:
                        perf["Altitude"] = round(alt)
                        if parameter in curves[wt]:
                            perf[parameter] = round(np.polyval(curves[wt][parameter],alt))
                        else:
                            perf[parameter] = "0"
                    aircraftProfile["ozRwy"][wt].append(perf)
    
    write_file(profiles_perf, "profiles_perf", "","ozacft")


profiles_perf = load_file("ozacft\\profiles_perf")
template_perf = load_file("ozacft\\template_perf")
AircraftPerformance_template = load_file("ozacft\\template_perf")




createPerf(profiles_perf)
test = pd.DataFrame(profiles_perf)
test
option = st.selectbox(
    'Select Profile',
    test,
    format_func=lambda x: "" + str(x)
    )

