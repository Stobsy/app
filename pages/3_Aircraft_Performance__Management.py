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



    if 'edit_perf_profile' not in st.session_state:
        st.session_state.edit_perf_profile = None


    globalVars = {
        "AL" : "4",
        "ozAltProfile" : np.linspace(5000, 45000, 9),
        "curvesToProcess" : ["ClimbTas","ClimbBurn","CruiseTas","CruiseBurn","ClimbRate"]
        #"curvesToProcess" : ["CruiseBurn"]
    }


    def create_database():
        st.markdown("# Create Database")
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
            
    def aircraft_manager():
        st.header("Aircraft Manager")
        con = db_util.con_db(config_file['database'])
        cur = con.cursor()
        aircraft_names = pd.read_sql("SELECT ID FROM aircraft", con)
        selected = st.selectbox("Aircraft",aircraft_names)

        aircraft = pd.read_sql("SELECT * FROM aircraft", con)
        st.info("To edit aircraft parameters please contact site adminsitrator - this functionality will be implimented at the user level soon")
        selected_data = aircraft.loc[aircraft['ID'].isin([selected])]
        selected_data
        st.subheader("All Aircraft Currently in " + config_file['database'])
        aircraft






















    def aircraft_importer():
        st.header("Aircraft Importer")
        here = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', ''))
        sqlite_dbs = [file for file in os.listdir(here + "\\db\\") if file.endswith('.db')]
        db_filename = st.selectbox('DB Filename', sqlite_dbs)
        con = db_util.con_db(db_filename)
        cur = con.cursor()
        existing_aircraft = pd.read_sql("SELECT * FROM aircraft", con)
        if not existing_aircraft.empty:
            existing_aircraft
            delete = st.button('Delete all aircraft in database')
            if delete:
                cur.execute('DELETE FROM aircraft;',)
                con.commit()
                st.success("All aircraft in the current database were deleted successfully")
        else:
            st.info("Currently no aircraft in the database")
        
        

        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            try:
                data = ast.literal_eval(stringio.read())
            except Exception as e:
                st.exception(e)
        
   
   

     
        st.warning("This will overwrite the aircraft currently contained in the aircraft database")
        populate = st.button('Populate aircraft from data file')

        if populate:
            added = []
            for ac in data:
       
                ac_pd = pd.Series(ac)
                if ((existing_aircraft['ID'] == ac_pd['ID'])).any():
                    pass
                else:
                    existing_aircraft = existing_aircraft.append(ac_pd,ignore_index=True)
                    added.append(ac_pd["ID"])
                
            existing_aircraft = existing_aircraft.astype('str')
            check = existing_aircraft.to_sql("aircraft", con,  if_exists='replace', index = False)
            if added:
                st.success("The following aircraft were added to the database")
                st.dataframe(added)
            else:
                st.error("No aircraft were added")
                    


                #sqlite_insert_with_param = "INSERT INTO aircraft (ID) VALUES (?);"
                #data_tuple = (ac["ID"],)
                #cur.execute(sqlite_insert_with_param, data_tuple)

                #for k, v in ac.items():
                #    try:
                #        add = ("ALTER TABLE aircraft ADD COLUMN " + k + "")
                #        cur.execute(add)
                #        con.commit()
                #    except Exception as e:
                #        st.exception(e)
                #    if type(v) is list or type(v) is dict:
                #        value = str(v)
                #    else:
                #        value = v
                #    this = ('UPDATE aircraft set ' + str(k) + ' = "' + str(value) + '" where ID = "' + ac["ID"] + '"')
                #    cur.execute(this)
                #con.commit()
            
        #cur.execute("SELECT * FROM aircraft")
        #names = list(map(lambda x: x[0], cur.description))
        #names = [description[0] for description in cur.description]
        # names
        
        con.close()
            #add = ("INSERT INTO aircraft VALUES('" + ac["ID"] + "')")
            #add
            #cur.executemany(add)
            #con.execute("UPDATE STUDENTS set SNAME = 'sravan' where SID = 1")


                
                
    def db_view():
        st.header("Database Viewer")

        here = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', ''))
        sqlite_dbs = [file for file in os.listdir(here + "\\db\\") if file.endswith('.db')]
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

        

    def get_blank_from_dtype(dtype):
        """Return correct values for the new line: 0 if column is numeric, "" if column is object, ..."""
        if is_numeric_dtype(dtype):
            return 0
        elif is_bool_dtype(dtype):
            return False
        else:
            return ""

  

    def delete_row(df, grid):
        selected_rows = grid['selected_rows']
        if selected_rows:
            selected_indices = [i['_selectedRowNodeInfo']
                                ['nodeRowIndex'] for i in selected_rows]
            df_indices = df.index[selected_indices]
            df = df.drop(df_indices)
        return df

    def load_table():
        pass

    def edit_data():

        st.header("Input or Edit Perf Data")
   

        con = db_util.con_db(config_file['performance']['database'])
        cur = con.cursor()

        current_profiles = pd.read_sql("SELECT * FROM perf_profiles", con)
        current_perf_data = pd.read_sql("SELECT * FROM perf_data", con)
        current_perf_data



        recorded_for = st.selectbox('Profile', current_profiles)
        id = current_profiles.loc[current_profiles['name'] == recorded_for]
        st.write(id.index[0])
        
        
    
   
        st.session_state.edit_perf_profile = current_perf_data.loc[current_perf_data['ID'] == id.index[0]]

           
        



        if st.session_state.edit_perf_profile.empty:
            st.error("No data for this profile")
            #t.session_state.edit_perf_profile = add_row(st.session_state.edit_perf_profile , rowid)

            st.session_state.edit_perf_profile = pd.DataFrame({'ID':id.index[0], 'Weight':0, 'Altitude':0, 'CruiseTas':0, 'CruiseBurn':0, 'ClimbTas':0, 'ClimbBurn':0, 'ClimbRate':0, 'TAT':0, 'SAT':0}, index=[0])

            #def add_row(df , rowid):
            #new_row = pd.DataFrame({'ID':rowid, 'Weight':0, 'Altitude':0, 'CruiseTas':0, 'CruiseBurn':0, 'ClimbTas':0, 'ClimbBurn':0, 'ClimbRate':0, 'TAT':0, 'SAT':0}, index=[0])
            #df = pd.concat([new_row,df.loc[:]]).reset_index(drop=True)





        
        gb = GridOptionsBuilder.from_dataframe(st.session_state.edit_perf_profile)
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True, hide = False)
        gb.configure_column("ID", hide = False, editable=False)
        gb.configure_column("TAT", hide = True)
        gb.configure_column("SAT", hide = True)
        gb.configure_selection('multiple', use_checkbox=False, groupSelectsChildren=True, groupSelectsFiltered=True)
        gb.configure_grid_options(domLayout='normal')
        gridOptions = gb.build()
    

        grid_response = AgGrid(
                        st.session_state.edit_perf_profile, 
                        gridOptions=gridOptions,
                        height=200, 
                        width='100%',
                        data_return_mode="AS_INPUT", 
                        update_mode=GridUpdateMode.GRID_CHANGED,
                        fit_columns_on_grid_load=True,
                        allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
                        enable_enterprise_modules=False
                )
        
        selected = grid_response['selected_rows']
        sss = pd.DataFrame(grid_response['data'])
        


        if st.button('Delete Selected Rows'):
            if grid_response['selected_rows']:
                st.session_state.edit_perf_profile = delete_row(st.session_state.edit_perf_profile, grid_response)
        
                st.experimental_rerun()
            else:
                st.error("No rows selected")


        if st.button('Add Row'):
            new_row = pd.DataFrame({'ID':id.index[0], 'Weight':0, 'Altitude':0, 'CruiseTas':0, 'CruiseBurn':0, 'ClimbTas':0, 'ClimbBurn':0, 'ClimbRate':0, 'TAT':0, 'SAT':0}, index=[0])
            st.session_state.edit_perf_profile = pd.concat([st.session_state.edit_perf_profile, new_row])

            st.experimental_rerun()
        with st.expander("Save Profile"):
            st.warning("Saving Profile will replace all data in the database for this profile - are you sure?")
            if st.button('Save Profile'):
                query = ("SELECT * FROM perf_data")
                full_db = pd.read_sql(query, con)
                full_db = full_db.drop(full_db.loc[full_db['ID'] == recorded_for].index, inplace=True)
                full_db = pd.concat([full_db, sss])
                check = full_db.to_sql("perf_data", con,  if_exists='replace', index = False)
                if check:
                    st.success("Data saved successfully")


        display_charts = st.multiselect('Charts to display', globalVars["curvesToProcess"])


        display_curve(sss, display_charts)




        





   


    def show_data():
        st.header("Show Data for Aircraft")
        con = db_util.con_db(config_file['database'])
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        cur.execute("SELECT name FROM perf_profiles")
        profile = cur.fetchall()  # get all the results from the above query
        recorded_for = st.selectbox('perf_profile', profile)
        cur.execute("SELECT rowid, * FROM perf_profiles WHERE name = ('" + recorded_for +"')")
        rowid = cur.fetchone()
        rowid
        con.close()
        con = db_util.con_db(config_file['database'])
        cur = con.cursor()
        cur.execute("SELECT * FROM perf_data WHERE ID=?", (rowid,))
        dataNew = cur.fetchall()
        wts = list(dict.fromkeys([rows[1] for rows in dataNew])) #get list of unique weights
        wts.sort()
        data = []
        for d in dataNew:
    
            template = dict({
                        "LoiterBurn": "0",
                        "CruiseTas": "0",
                        "ClimbTas": "0",
                        "CruiseBurn": "0",
                        "DescentBurn": "0",
                        "DescentTas": "0",
                        "ClimbRate": "0",
                        "Altitude": "0",
                        "DescentRate": "0",
                        "ClimbBurn": "0",
                        "HoldingBurn": "0",
                        "PlanTas": "0",
                        "TaxiBurn": "0",
                        "Weight": "0"
                    })
            
            template["Weight"] = str(d[1])
            template["Altitude"] = str(d[2])
            template["CruiseTas"] = str(d[3])
            template["CruiseBurn"] = str(d[4])
            template["ClimbTas"] = str(d[5])
            template["ClimbBurn"] = str(d[6])
            template["ClimbRate"] = str(d[7])
            data.append(template)
        
        


        curves = {}
        for i , wt in enumerate(wts):
            curves[wt]={}
            
            for parameter in globalVars["curvesToProcess"]:
                dataPoints = list(filter(lambda item: item['Weight'] == str(wt), data))
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
        #st.subheader("curves")
        #curves

        number =  len(wts)
        

        for n , parameter in enumerate(globalVars["curvesToProcess"]):
            st.subheader(parameter)
            fig, axes = plt.subplots()
            is_data = False
            for i , wt in enumerate(wts):
                rgb = tuple(colorsys.hsv_to_rgb(i/number, 1, 1))
                dataPoints = list(filter(lambda item: item['Weight'] == str(wt), data))
                x = []
                y = []

                for dataPoint in dataPoints:
                    if dataPoint[parameter] != "0" and dataPoint["Altitude"] != "0":
                        x.append(dataPoint["Altitude"])
                        y.append(dataPoint[parameter])
                        #convert list of str to integers
                
                    #check there is somthing in x and y
                
                if x and y:
                    is_data = True
                    x = [int(numeric_string) for numeric_string in x]
                    y = [int(numeric_string) for numeric_string in y]
                    #fit the curve
                    xFit, yFit, curve = curveFit(x,y,3)
                    minn = min(x)
                    maxx = max(x) 
                    x2 = np.linspace(minn, maxx, num=30)
                    y2 = np.polyval(curve,x2)
                    axes.plot(x, y, color=rgb, marker="+" , linestyle='none', linewidth=2, markersize=8,)
                    axes.plot(x2, y2, color=rgb ,label= wt, linewidth=1)
                    
                    axes.set_xlabel('Altitude')
                    axes.set_ylabel(parameter)
                    axes.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
                    axes.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
                    axes.legend(title='Weights:', prop={'size': 10}, loc='upper right')
                    
            
            if is_data:
                st.plotly_chart(fig)
            else:
                st.error("No Data")











        st.subheader("perf_data")
        query = ("SELECT * FROM perf_data WHERE ID="+ str(rowid) + "")
        test = pd.read_sql(query, con)
        test



    
        #rows = []
        #for row in cur.execute("SELECT name FROM perf_data ORDER BY name"):
        #    rows.append(row[0])
    


    def upload_data():
        st.markdown("# Upload Data")
        # https://discuss.streamlit.io/t/uploading-csv-and-excel-files/10866/2
        here = os.path.dirname(os.path.realpath(__file__))
        sqlite_dbs = [file for file in os.listdir(here + "\\db\\") if file.endswith('.db')]
        db_filename = st.selectbox('DB Filename', sqlite_dbs)
        data_files = [file for file in os.listdir(here + "\\data\\") if file.endswith('.txt')]
        data_filename = st.selectbox('DB Filename', data_files)
        data_filename

        data = file_util.load_file(data_filename, "\\data\\")
        data

        status , con = db_util.con_db(db_filename , here + "\\db\\")
        if status:
            st.error(status)
            return
        cur = con.cursor()
        try:
            cur.execute("CREATE TABLE movie(title, year, score)")
        except Exception as e:
            e
            st.write(e)
        res = cur.execute("SELECT name FROM sqlite_master")
        res.fetchone()
        cur.execute("""
        INSERT INTO movie VALUES
            ('Monty Python and the Holy Grail', 1975, 8.2),
            ('And Now for Something Completely Different', 1971, 7.5)
    """)
        con.commit()
        res = cur.execute("SELECT score FROM movie")
        res.fetchall()
        res



        #uploaded_file = st.file_uploader('Choose a file')
        #if uploaded_file is not None:
        #    #read csv
        #    try:
        #        df = pd.read_csv(uploaded_file)
        #        df.to_sql(name=table_name, con=conn)
        #        st.write('Data uploaded successfully. These are the first 5 rows.')
        #        st.dataframe(df.head(5))

        #    except Exception as e:
        #        st.write(e)


    def perf_importer():
        st.header("Performance Data Importer")
 

        con = db_util.con_db(config_file['performance']["database"])
        cur = con.cursor()
        current_profiles = pd.read_sql("SELECT * FROM perf_profiles", con)
        current_perf_data = pd.read_sql("SELECT * FROM perf_data", con)



        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            try:
                data = ast.literal_eval(stringio.read())
            except Exception as e:
                st.exception(e)

        action = st.radio(
        "How is data to be incorperated",
    ('Add', 'Replace', 'New Profile'))

        if action == 'Add' or action == 'Replace':
            
            profile = st.selectbox('Profile to replace or add data', current_profiles)
            id = current_profiles.index[current_profiles['name'] == profile].tolist()[0]
            
            
        else:
            new_name = st.text_input('New Profile Name', '')
      
        
        

        if st.button('Commit to changes'):
            if action == 'New Profile':
                d = {'name': [new_name]}
                d = pd.DataFrame(d)
                st.dataframe(d)
                new_profiles = pd.concat([current_profiles, d], ignore_index = True)
                st.info("Dfd")

                new_profiles
                id = new_profiles.index[-1]
                new_profiles.to_sql("perf_profiles", con,  if_exists='replace', index = False)
            elif action == 'Replace':
                current_perf_data.drop(current_perf_data.loc[current_perf_data['ID']==id].index, inplace=True)
            
            for d in data:
           
                insert_row = {"ID":id, "Weight":d[0], "Altitude":d[1], "CruiseTas":d[2], "CruiseBurn":d[3], "ClimbTas":d[4], "ClimbBurn":d[5], "ClimbRate":d[6]}

                insert_row = pd.DataFrame([insert_row])
   
                current_perf_data = pd.concat([current_perf_data, insert_row], ignore_index = True)
 
                #(ID, Weight, Altitude, CruiseTas, CruiseBurn, ClimbTas, ClimbBurn, ClimbRate, TAT, SAT)
                current_perf_data.to_sql("perf_data", con,  if_exists='replace', index = False)



            
        current_perf_data = pd.read_sql("SELECT * FROM perf_data", con)
        current_perf_data
        con.close()

        #    if name:
        #        try:
        #            
        #            insert = [(name, str(data))] #eval()
        #            cur.execute("SELECT name FROM perf_data_sets WHERE name = ?", (name,))
        #            checks = cur.fetchall()
        #            if checks:
        #                st.error("profile already exists")
        #            else: 
        #                cur.executemany("INSERT INTO perf_data_sets VALUES(?, ?)", insert)
        #                con.commit()
        #                st.success("added successfully")
        #                for row in cur.execute("SELECT name, data FROM perf_data_sets ORDER BY name"):
        #                    st.write(row)
        #        except Exception as e:
        #            e
        #    else:
        #        st.error("perf_data_set name can't be blank")

        
        
    def curveFit(x , y, poly):
        xn = np.linspace(min(x), max(x), 50)
        popt = np.polyfit(x, y, poly)
        yn = np.polyval(popt, xn)
        return (xn , yn, popt)


    def display_curve(data, charts):

        #get unique weights from dataset
        data = data.drop(data.loc[data['Weight'] == 0].index, inplace=False)
        data = data.drop(data.loc[data['Altitude'] == 0].index, inplace=False)
        wts = data.loc[:,"Weight"]
        wts = wts.drop_duplicates()
        wts = wts.values.tolist()
        wts.sort()
        number =  len(wts)
        


        
            
        for parameter in charts:
            st.subheader(parameter)
            fig, axes = plt.subplots()
            axes.set_xlabel('Altitude')
            axes.set_ylabel(parameter)
            axes.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
            axes.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
            
            
            
            curves = {}
            is_plot = False
            for i , wt in enumerate(wts):
                axes.legend(title='Weights:', prop={'size': 10}, loc='upper right')
            
                rgb = tuple(colorsys.hsv_to_rgb(i/number, 1, 1))
                curves[wt]={}
                
                data_points = data.drop(data.loc[data['Weight'] != wt].index, inplace=False)
            
                x = []
                y = []
                for i in range(len(data_points)):
                    data_point = data_points.iloc[i][parameter]
                    
                    if data_point != "0":
            
                        x.append(data_points.iloc[i]['Altitude'])
                        y.append(data_point)
                        #convert list of str to integers
                        x = [int(numeric_string) for numeric_string in x]
                        y = [int(numeric_string) for numeric_string in y]

                        #check there is somthing in x and y
                
                if x and y:
                    is_plot = True
                    #fit the curve
                    xFit, yFit, curve = curveFit(x,y,3)
                    curves[wt][parameter]=curve
                    minn = min(x)
                    maxx = max(x) 
                    x2 = np.linspace(minn, maxx, num=30)
                    y2 = np.polyval(curve,x2)
                    axes.plot(x, y, color=rgb, marker="+" , linestyle='none', linewidth=2, markersize=8,)
                    axes.plot(x2, y2, color=rgb ,label= wt, linewidth=1)
                            
            if is_plot:                
                st.plotly_chart(fig)
            else:
                st.error("No data")

        



    page_names_to_funcs = {
        "Performance Data Importer": perf_importer,
        "Input or Edit Perf Data": edit_data,
        "Show Perf Data": show_data,
    }

    selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
    page_names_to_funcs[selected_page]()
