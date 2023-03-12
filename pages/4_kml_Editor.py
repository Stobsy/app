
import streamlit as st
import numpy as np
import pandas
from pandas import DataFrame
# For Flair (Keybert)
import plotly.graph_objects as go
from shapely.geometry import Polygon, LineString, Point, mapping
# For download buttons
import copy
import os
import json
import pandas as pd
from geopy.geocoders import ArcGIS, Nominatim
from geopy import Point
from util import shapeutilities
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode



from util import db_util
from util import file_util
from util import auth
from config import config
import sqlite3
from exceptiongroup import ExceptionGroup, catch



name, authentication_status, username = auth.check()

if username != 'stobsy' and username != 'admin':
    st.error('This page is for admin users only')
else:
    config_file = config.load_config_file()



    if 'shapes' not in st.session_state:
        st.session_state.shapes = {}
    if 'inputText' not in st.session_state:
        st.session_state.inputText = ""
    if 'shapeEdit' not in st.session_state:
        st.session_state.shapeEdit = {}
    if 'kmlEdit' not in st.session_state:
        st.session_state.kmlEdit = []


    if 'kml_project' not in st.session_state:
        st.session_state.kml_project = None


    if 'count' not in st.session_state:
        st.session_state.count = 0









    def _max_width_():
        max_width_str = f"max-width: 1400px;"
        st.markdown(
            f"""
        <style>
        .reportview-container .main .block-container{{
            {max_width_str}
        }}
        </style>    
        """,
            unsafe_allow_html=True,
        )


    _max_width_()






    def input():
        st.header("Input Points to Project")
        con = db_util.con_db(config_file['database'])
        cur = con.cursor()
        message = st.container()
        if st.session_state.kml_project == None:
            pass
            message.error("No project selected, please select of add a project from 'Project Manager'")
        else:
            message.info("Current Project:  " + st.session_state.kml_project['name'])

            if st.button("Load Test Data"):
                st.session_state.kml_project['data']  = shapeutilities.init_data(test = True)
            if st.button("Reset Data"):
                st.session_state.kml_project['data']  = shapeutilities.init_data()
                #st.write(st.session_state.kml_project['data'].dtypes)
    



            gb = GridOptionsBuilder.from_dataframe(st.session_state.kml_project['data'])
            gb.configure_default_column(editable=True, hide = True)
            #gb.configure_default_column(rowDrag = True, rowDragManaged = True, rowDragEntireRow = True, rowDragMultiRow=True)
            #gb.configure_column('Index', rowDrag = False, rowDragEntireRow = True,editable=True, width = 30)
            gb.configure_column('name', rowDrag = False, rowDragEntireRow = True,editable=True, hide = False)
            gb.configure_column('point_text', headerName = "Text to Import" , editable=True, hide = False)
            gb.configure_column('string', headerName = "Coordinates", editable=False, hide = False)
            gb.configure_selection('multiple', use_checkbox=False, groupSelectsChildren=True, groupSelectsFiltered=True) 
            gb.configure_grid_options(domLayout='normal')
            gridOptions = gb.build()
            inputData = AgGrid(st.session_state.kml_project['data'],
                        gridOptions=gridOptions,
                        width='100%',
                        height = 400,
                        data_return_mode="AS_INPUT", 
                        update_mode=GridUpdateMode.GRID_CHANGED,
                        fit_columns_on_grid_load=True ,
                        allow_unsafe_jscode=False,
                        enable_enterprise_modules=False
                        )
            #selected = inputData['selected_rows']
            data = inputData['data']
            st.session_state.kml_project['data'] = data

            #data['point_text'].replace('', np.nan, inplace = True)
       



            try:
                results = shapeutilities.parseCell(data)
                st.session_state.kml_project['data'] = results
                message.success('Points processed without errors, please review data below and click save')

                if 1 == 2:
                    gb = GridOptionsBuilder.from_dataframe(results)
                    gb.configure_default_column(editable=False)
                    gb.configure_column('lat',  type=['numericColumn','numberColumnFilter','customNumericFormat'] ,precision=5)
                    gb.configure_column('lon',  type=['numericColumn','numberColumnFilter','customNumericFormat'] ,precision=5) 
                    gb.configure_grid_options(domLayout='normal')
                    gridOptions = gb.build() 
                    inputData = AgGrid(results,
                                gridOptions=gridOptions,
                                width='100%',
                                data_return_mode="AS_INPUT", 
                                update_mode=GridUpdateMode.GRID_CHANGED,
                                fit_columns_on_grid_load=True ,
                                allow_unsafe_jscode=False,
                                enable_enterprise_modules=True
                                )
                    selected = inputData['selected_rows']
                    data = inputData['data']
                


            except Warning as e:
                locations = []
                st.error('Errors occured at the following rows; please review the data')
                for a in e.indexes:
                    locations.append(a[0])
                for index, row in st.session_state.kml_project['data'].iloc[locations].iterrows():
                    st.error("Row " + str(index+1) + " name: " + row['name'] + ", position string: " + row['point_text'])
                    



             
    
        
            
            
             
                
    
        con.close()





    def shape_edit():
        st.header('Shape Editor')
        st.subheader("Add, subtract or edit solid shapes like circles or polygons")

       

        
    
        operator = st.radio(
                    "Operation",
                    ["Add", "Subtract" , "Slice" , "Interior Buffer", "Exterior Buffer"],
                    help="-   For polygons do not re-enter the start point\n-   Use lines as to cut polygons in editing actions",
                )

        #st.write(obj1['points'])
        shapeName = st.text_input("Shape Name")
        new_points = shapeutilities.init_table(rows = 0)

        match operator:
           
            case "Add":
                
            
                #filtered = filter(lambda type: type == "Polygon" | "Circle", shapes['type'])
                shapes = copy.deepcopy(st.session_state.kml_project['shapes'])
                filtered = [shape for shape in shapes if shape['type'] == 'Line']
                st.write(filtered)
                shape1 = st.selectbox("1", filtered['name'])
                shape2 = st.selectbox("2", filtered['name'])
                obj1 = copy.deepcopy(shapes[shape1])
                obj2 = copy.deepcopy(shapes[shape2])

                new_poly = obj1['poly'].union(obj2['poly'])
                lat_l = []
                lon_l = []
                for lat, lon in new_poly.exterior.coords:
                    lat_l.append(lat)
                    lon_l.append(lon)
                new_points['lat'] = lat_l
                new_points['lon'] = lon_l
            case "Subtract":
                new_poly = obj1['poly'].difference(obj2['poly'])
                lat_l = []
                lon_l = []
                for lat, lon in new_poly.exterior.coords:
                    lat_l.append(lat)
                    lon_l.append(lon)
                new_points['lat'] = lat_l
                new_points['lon'] = lon_l
            case "Slice":

                buff_line = obj2['poly'].buffer(0.001)  #is polygon
                halves = obj1['poly'].difference(buff_line)
                part = st.radio(
                    "Part",
                    range(0, len(halves.geoms)),
                    help="-   For polygons do not re-enter the start point\n-   Use lines as to cut polygons in editing actions",
                )
                new_poly = halves.geoms[part]
                #new_poly = obj1['poly'].difference(obj2['poly'])
                lat_l = []
                lon_l = []
                for lat, lon in new_poly.exterior.coords:
                    lat_l.append(lat)
                    lon_l.append(lon)
                new_points['lat'] = lat_l
                new_points['lon'] = lon_l
 
          

   
        colorLine = st.color_picker('Line Colour')
        colorFill = st.color_picker('Fill Colour')
        colorFillAlpha = st.slider('Opacity',  min_value=0, max_value=100, value=50, step = 10)
        shape = shapeutilities.make_shape(new_points, type="Polygon", name = shapeName, linecolor = colorLine, fillColor = colorFill, opacity = colorFillAlpha)
    
        obj1['opacity'] = 10
        obj2['opacity'] = 10
      
        fig = shapeutilities.draw_shapes([obj1, obj2, shape])
        test = st.plotly_chart(fig, use_container_width=True)


     
    def shapes():
        st.header("Create Shapes")        
        st.subheader("Select Points for Shape")
        if st.session_state.kml_project['shapes'] == None:
            st.session_state.kml_project['shapes'] = []
        gb = GridOptionsBuilder.from_dataframe(st.session_state.kml_project['data'])
        gb.configure_default_column(editable=False, hide = True)
        #gb.configure_default_column(rowDrag = True, rowDragManaged = True, rowDragEntireRow = True, rowDragMultiRow=True)
        #gb.configure_column('Index', rowDrag = False, rowDragEntireRow = True,editable=True, width = 30)
        gb.configure_column('name', rowDrag = False, rowDragEntireRow = True,editable=False, hide = False)
        gb.configure_column('point_text', editable=True, hide = True)
        gb.configure_column('string', headerName = "Coordinates", editable=False, hide = False)
        gb.configure_selection('multiple', use_checkbox=False, groupSelectsChildren=True, groupSelectsFiltered=True) 
        gb.configure_grid_options(domLayout='normal')
        gridOptions = gb.build()

        inputData = AgGrid(st.session_state.kml_project['data'],
                    gridOptions=gridOptions,
                    width='100%',
                    height = 400,
                    data_return_mode="AS_INPUT", 
                    update_mode=GridUpdateMode.GRID_CHANGED,
                    fit_columns_on_grid_load=True ,
                    allow_unsafe_jscode=False,
                    enable_enterprise_modules=True
                    )
        selected = pd.DataFrame(inputData['selected_rows'])
        data = pd.DataFrame(inputData['data'])
        st.session_state.layer = selected




        if st.session_state.layer.empty:
            st.error("No points seleted")
        else:
            col1, col2 = st.columns(2)
            with col1:
                gb1 = GridOptionsBuilder.from_dataframe(st.session_state.layer)
                gb1.configure_default_column(editable=False, hide = True)
                gb1.configure_column('name', hide = False, rowDrag=True)
                gb1.configure_column('string',hide = True)
                #gb1.configure_selection('multiple', use_checkbox=False, groupSelectsChildren=True, groupSelectsFiltered=True) 
                gb1.configure_grid_options(rowDragManaged = True, rowDragEntireRow = True, rowDragMultiRow = True)

            
                gridOptions = gb1.build()
                inputData1 = AgGrid(st.session_state.layer,
                            gridOptions=gridOptions,
                            width='100%',
                            data_return_mode="AS_INPUT",
                            update_on=['rowDragEnd'],
                            update_mode=GridUpdateMode.MODEL_CHANGED,
                            fit_columns_on_grid_load=True ,
                            allow_unsafe_jscode=False,
                            enable_enterprise_modules=True,
                            reload_data=False
                            )
        
                selected = pd.DataFrame(inputData1['selected_rows'])
                data = pd.DataFrame(inputData1['data'])
                
         


            with col2:
                pass

            ccol1, ccol2 = st.columns(2)
            with ccol1:
                shapeName = st.text_input("Shape Name")
                add_button = st.button("Add to Shapes")

            with ccol2:
                
                shapeType = st.radio(
                    "Set your shape type",
                    ["Points", "Line" , "Polygon" , "Circle"],
                    help="-   For polygons do not re-enter the start point\n-   Use lines as to cut polygons in editing actions",
                )

            error = st.empty()
                
            with st.expander("Shape Options", expanded=False):

                match shapeType:
                    case "Points":
                        st.subheader("For Points")
                        col1, col2 = st.columns(2)
                        with col2:
                        
                            st.markdown("Select icon to be used for points on *kml.\n\nNote: icon will not display on represenation below but will on the .kml file")
                        
                            from st_clickable_images import clickable_images
                            images_list = [
                            "placemark_circle",
                            "airports",
                            "donut",
                            "forbidden",
                            "marina",
                            "open-diamond",
                            "placemark_circle",
                            "placemark_circle_highlight",
                            "placemark_square",
                            "placemark_square_highlight",
                            "polygon",
                            "square",
                            "star",
                            "target",
                            "triangle"
                            ]
                            clickable_images_list = []
                            for image in images_list:
                                image_link = "http://maps.google.com/mapfiles/kml/shapes/"+ image + ".png"
                                clickable_images_list.append(image_link)
                        
                            
                            clicked = clickable_images(
                                clickable_images_list,
                                titles=images_list,
                                div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                                img_style={"margin": "5px", "height": "50px"},
                            )

                            
                        
                        with col1:
                            st.markdown(".kml icon")
                            st.image(clickable_images_list[clicked], width = 50)
                            colorLine = st.color_picker('Line Colour')
                            colorFill = st.color_picker('Fill Colour')
                            shape = shapeutilities.make_shape(data, type="Points", name = shapeName, linecolor = colorLine , icon = clickable_images_list[clicked])
                            
                            
                           
                            
                    case "Line":
                        st.header("For a Line")
                        colorLine = st.color_picker('Line Colour')
                        shape = shapeutilities.make_shape(data, type="Line", name = shapeName,linecolor = colorLine)
      
                    case "Polygon":
                        st.header("For a Polygon")
                        colorLine = st.color_picker('Line Colour')
                        colorFill = st.color_picker('Fill Colour')
                        colorFillAlpha = st.slider('Opacity',  min_value=0, max_value=100, value=50, step = 10)
                        shape = shapeutilities.make_shape(data, type="Polygon", name = shapeName, linecolor = colorLine, fillColor = colorFill, opacity = colorFillAlpha)
                    
                    case "Circle":
                        st.header("For a Circle")
                        if len(data) > 1:
                            error.error("Please process one point at a time for a circle")
                            shape = None
                        else:
                            radius = st.text_input("Radius (Nm)", "15")
                            colorLine = st.color_picker('Line Colour')
                            colorFill = st.color_picker('Fill Colour')
                            colorFillAlpha = st.slider('Opacity',  min_value=0, max_value=100, value=50, step = 10)
                            xx, yy = shapeutilities.polyCircle(data , radius)
                            x = xx.tolist()
                            y = yy.tolist()
                            data = pd.DataFrame({"lat":y,'lon':x,'name':None})
                            shape = shapeutilities.make_shape(data, type="Circle", name = shapeName, linecolor = colorLine, fillColor = colorFill, opacity = colorFillAlpha)
             


                if add_button:
                    if shapeName != "":
                        shape['name'] = shapeName
                    st.session_state.kml_project['shapes'].append(copy.deepcopy(shape))
            

                  
           

            

            if st.button("Create .kml"):
                shapeutilities.createKML(st.session_state.kml_project['shapes'], "test")
            if st.button("Clear Shapes"):
                st.session_state.kml_project['shapes'] = []
            
            fig = shapeutilities.draw_shapes(st.session_state.kml_project['shapes'] , temp = shape)
            test = st.plotly_chart(fig, use_container_width=True)
            


 
                
           
            
            #fig.add_trace(trace)
            #fig.update_traces(
            #    textposition='top center',
            #    marker=[{'source': clickable_images_list[clicked],
            #    'x': 0.5, 'y': 0.5, 'xref': 'paper', 'yref': 'paper', 'sizex': 0.3, 'sizey': 0.3,
            #    'visible': True, 'layer': "above"}]
            #    )
            #test = st.plotly_chart(fig, use_container_width=True)








    def temp():



        if not st.session_state.Collection.dataFrame.empty:
            
    
            st.subheader("Shape Settings")
            name = st.text_input('Name of Line / Polygon or collection of Circles / Points', 'New Shape')
            st.session_state.Collection.name = name
            
            match shapeType:
                case "Points":
                    st.session_state.Collection.type = "points"
                    st.subheader("For Points")
                    col1, col2 = st.columns(2)
                    with col2:
                    
                        st.markdown("Select icon to be used for points on *kml.\n\nNote: icon will not display on represenation below but will on the .kml file")
                    
                        from st_clickable_images import clickable_images
                        images_list = [
                        "placemark_circle",
                        "airports",
                        "donut",
                        "forbidden",
                        "marina",
                        "open-diamond",
                        "placemark_circle",
                        "placemark_circle_highlight",
                        "placemark_square",
                        "placemark_square_highlight",
                        "polygon",
                        "square",
                        "star",
                        "target",
                        "triangle"
                        ]
                        clickable_images_list = []
                        for image in images_list:
                            image_link = "http://maps.google.com/mapfiles/kml/shapes/"+ image + ".png"
                            clickable_images_list.append(image_link)
                        
                        clicked = clickable_images(
                            clickable_images_list,
                            titles=images_list,
                            div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                            img_style={"margin": "5px", "height": "50px"},
                        )

                        #st.markdown(f"Image {images_list[clicked]} clicked" if clicked > -1 else "No image clicked")
                    with col1:
                        st.markdown("Selected .kml icon")
                        st.image(clickable_images_list[clicked], width = 50)
                        st.session_state.Collection.icon = clickable_images_list[clicked]
        
                        colorLine = st.color_picker('Line Colour')
                        #colorFill = st.color_picker('Fill Colour', editShape.colorFill)

                        st.session_state.Collection.colorLine = colorLine
                        #editShape.colorFill = colorFill
            
                        #gb = GridOptionsBuilder.from_dataframe(st.session_state.workSpaceData)
                        #gb.configure_default_column(editable=True)
                        #gridOptions = gb.build()
                        #tempo = AgGrid(st.session_state.workSpaceData, gridOptions=gridOptions, key='an_unique_key', update_mode='VALUE_CHANGED')
                        #editShape.data = tempo['data']
                        #df = tempo['data']
                        #editShape.data = tempo['data']

            
                    
                case "Line":
                    st.header("For a Line")
                    editShape = shapeutilities.ALine(copy.copy(st.session_state.workSpaceData))
                    tempo = editShape.table()
                    tempo
                    colorLine = st.color_picker('Line Colour', editShape.color)
                    editShape.color = colorLine

                case "Polygon":
                    print("poly")
                    closePoly = copy.copy(st.session_state.workSpaceData)
                    temp = closePoly.loc[0]
                    closePoly.loc[len(closePoly.index)] = temp
                    editShape = shapeutilities.APolygon(closePoly)
                    tempo = editShape.table()
                    tempo
                    colorLine = st.color_picker('Line Colour', editShape.color)
                    editShape.color = colorLine



                case "Circles":
                    st.header("For Circles")
                    editShape = shapeutilities.ACircle(copy.copy(st.session_state.workSpaceData))
                    tempo = editShape.table()
                    tempo
                    editCircle = shapeutilities.ACircle(tempo['data'])
                    colorLine = st.color_picker('Line Colour', editShape.color)
                    editShape.color = colorLine


        fig = go.Figure()
        fig.update_xaxes(
            showticklabels=False,
            showgrid=False
            )
        fig.update_yaxes(
            showticklabels=False,
            showgrid=False,
            scaleanchor = "x",
            scaleratio = 1,
            )
        fig.update_traces(
            textposition='top center'
            )
        fig.update_layout(
            #width=kwargs.get("size"),
            #height=kwargs.get("size"),
            autosize=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10)
            )

        
        fig.add_trace(st.session_state.Collection.trace())
        test = st.plotly_chart(fig, use_container_width=True)














    def project_manager():
        st.header("kml Project Manager")



        con = db_util.con_db(config_file['database'])
        cur = con.cursor()

        if st.button("Delete all projects"):
            cur.execute("DELETE FROM kml_projects")
            con.commit()


        projects = pd.read_sql("SELECT * FROM kml_projects", con)



        new_name = st.text_input("New Project Name")
        new_description = st.text_input("New Project Description")
        new_notes = st.text_input("New Project Notes")
        if st.button("Create New Project"):
            if  (projects['name'] == new_name).any():
                st.error("Project " + new_name + " already exists")
            else:
                new = {'name' : new_name, 'description' : new_description , 'notes' : new_notes, 'user':0, 'data':None, 'shapes':None}
                new_DataFrame = pd.DataFrame(new, index=[0])

               
      
                projects = pd.concat([projects, new_DataFrame], ignore_index = True)
                try:
                    projects.to_sql("kml_projects", con,  if_exists='replace', index = False)
                    st.success("Project created successfully")
                except Exception as e:
                    e
        
        if projects.empty:
            st.error("Currently no projects in the database, create a new one below")
           
        else:
            project_index = st.selectbox('Working Project',  range(len(projects)), format_func=lambda x: projects.loc[x]['name'])
  
            if st.button("Select Project"):
                st.session_state.kml_project = projects.loc[[project_index]].to_dict(orient='records')[0]
                
        

           
            if  st.session_state.kml_project:
                st.info("Selected project is " + st.session_state.kml_project['name'])
      
            else:
                st.info("No project selected")
        
    




        
  
        

        con.close()


        #index = projects.index[projects['name'] == project].tolist()
        #df.iloc[i]
        #df.loc[idx]



    page_names_to_funcs = {
        "Project Manager":project_manager,
        "Input Points": input,
        "Create Shapes": shapes,
        "Shape Editor": shape_edit,
    }

    selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
    page_names_to_funcs[selected_page]()

            