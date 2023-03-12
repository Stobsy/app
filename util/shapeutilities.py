from shapely.geometry import Point
import pyproj
from pyproj import Transformer
from shapely.ops import transform
import simplekml
from shapely.geometry import Polygon, LineString, Point, mapping
import simplekml
import math
import os
from os import walk
import ast
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from ast import literal_eval
from geopy import Point as GeoPoint
import sqlite3
from datetime import date, time, datetime
import copy
from functools import partial
import matplotlib.colors
from exceptiongroup import ExceptionGroup, catch
import numpy as np






def get_poly(shape):

    match shape['type']:

        case "Points": #points
            Point(shape['points'])

        case "Line": #line
            self.polyPoints = self.points
            self.poly = self.polyLine(self.points)

        case "Polygon": #poly
            self.polyPoints = self.points
            self.poly = self.polyPoly(self.points)

        case "Circle": #circle
        
            self.poly = self.polyCircle(self.points, self.circleRadius)


def polyCircleA(self , coords , radius):
        # Buckingham Palace, London
        lat = coords[0][0]
        lng = coords[0][1]
        radius = int(radius) * 1852  # radius in meters
        local_azimuthal_projection = "+proj=aeqd +R=6371000 +units=m +lat_0={} +lon_0={}".format(lat, lng)
        wgs84_to_aeqd = Transformer.from_proj('+proj=longlat +datum=WGS84 +no_defs',local_azimuthal_projection)
        aeqd_to_wgs84 = Transformer.from_proj(local_azimuthal_projection,'+proj=longlat +datum=WGS84 +no_defs',always_xy = False)
        # Get polygon with lat lon coordinates
        point_transformed = Point(wgs84_to_aeqd.transform(lng, lat))
        buffer = point_transformed.buffer(radius, resolution=32)
        circle = transform(aeqd_to_wgs84.transform, buffer)
        self.polyPoints = list(circle.exterior.coords)
        tcircle = [t[::-1] for t in self.polyPoints]
        self.polyPoints = tcircle
        return  Polygon(tcircle)
        


def polyLine (self , coords):
    return LineString(coords)

def polyPoly (self, coords):
    coords.append(coords[0])
    return  Polygon(coords)


def createKML(shapes, name):

    kml = simplekml.Kml()
    for shape in shapes:
        lr, lg, lb = matplotlib.colors.to_rgb(shape['linecolor'])
        fr, fg, fb = matplotlib.colors.to_rgb(shape['fillcolor'])

     
        
        print(shape['type'])
        if shape['type'] == "Points":
  
            for index, point in shape['points'].iterrows():
            
     
                pnt = kml.newpoint()
                pnt.name = point['name']
                lon = point['lon']
                lat = point['lat']
                pnt.style.iconstyle.scale = 0.5  # Icon thrice as big
                pnt.style.iconstyle.icon.href = shape['icon']
                pnt.style.balloonstyle.text = point['name']
                pnt.coords = [(lon,lat)]



        elif shape['type'] == "Line":
   
            points_data = shape['points'][['lon', 'lat']]
            points = list(points_data.itertuples(index=False))
            ls = kml.newlinestring(name=name)
            ls.coords = points
            ls.extrude = 1
            ls.altitudemode = simplekml.AltitudeMode.relativetoground
            ls.style.linestyle.width = 50
            
            ls.style.linestyle.color = simplekml.Color.rgb(int(lr)*255,int(lg)*255,int(lb)*255)

        else:
            points_data = shape['points'][['lon', 'lat']]
            points = list(points_data.itertuples(index=False))
            ls = kml.newpolygon(name=name)
            ls.outerboundaryis = points
            ls.altitudemode = simplekml.AltitudeMode.relativetoground
            ls.style.linestyle.width = 50
            ls.style.polystyle.fill = True
            
            ls.style.linestyle.color = simplekml.Color.rgb(int(lr)*255,int(lg)*255,int(lb)*255)

            fill = simplekml.Color.rgb(int(fr)*255,int(fg)*255,int(fb)*255)
            st.write(fill)
            st.write(shape['opacity'])
            opacity = int((shape['opacity']/100)*255)
            st.write(opacity)
            filla = simplekml.Color.changealphaint(opacity, fill)
            st.write(filla)
            ls.style.polystyle.color = filla





    
    kml_string = kml.kml(format=True)
    st.download_button("Download .kml", kml_string, file_name="test.kml")

def init_table(*args, **kwargs):
    rows = kwargs.get('rows', 100)
    table = pd.DataFrame({'name':[""]*rows, 'point_text': [""]*rows, 'lat':[""]*rows, 'lon':[""]*rows, 'string':[""]*rows})
    return table

def init_data(*args, **kwargs):
    loadTestData = kwargs.get('test', False)
    data = init_table()

    if loadTestData :
        new_data = pd.DataFrame({
            'name':[ 
"test1",
"test2",
"test3",
"test4",
"test5",
"test6",
"test7",
"test8",
        ],
            'point_text':[
"""21 59' 50" S 151 00' 20" E""",
"""22 02' 50" S 151 11' 15" E""",
"""22 51' 54" S 152 27' 13" E""",
"""23 38' 40" S 153 06' 40" E""",
"""24 20' 55" S 152 05' 00" E""",
"""23 46' 10" S 151 40' 00" E""",
"""22 49' 22" S 150 47' 07" E""",
"""22 41' 19" S 150 50' 31" E"""
    ]
})
        #st.write(data[['name','point_text']].loc[:7])
        #st.write(new_data)
        data.loc[:7, ['name','point_text']] = new_data


    return data


def lat(s):
    try:
        p = GeoPoint.from_string(s)
        return p.latitude
    except Exception as e:
        return e

def lon(s):
    try:
        p = GeoPoint.from_string(s)
        return p.longitude
    except Exception as e:
        return e

def str(s):
    try:
        p = GeoPoint.from_string(s)
        return p.format_unicode()
    except Exception as e:
        return e


def convert(x):
    d = int(x)
    ms = x - d
    ms = ms*60
    ms = round(ms, 4)

    return d, ms

    
def parseCell(data):
    errors = []
    for index, row in data.iterrows():
        if row['point_text'] != "":
            try:
                p = GeoPoint.from_string(row['point_text'])
                row['lat'] = p.latitude
                lat_d, lat_m = convert(p.latitude)
                lat_s = "S" if lat_d < 0 else "N"
                lat_d = abs(lat_d)
                row['lon'] = p.longitude
                lon_d, lon_m = convert(p.longitude)
                lon_s = "W" if lon_d < 0 else "E"
                lon_d = abs(lon_d)
   
                row['string'] = ("%s\u00B0 %sm %s, %s\u00B0 %sm %s" % (lat_d,lat_m,lat_s,lon_d,lon_m, lon_s))
       
                #row['string'] = p.format(altitude=None, deg_char='', min_char='m', sec_char='s')
            except Exception as e:
                row['string'] = "error"
                errors.append((index, e))
    if errors:
        send = Warning()
        send.indexes = errors
        raise send
    return data


def parseData(data):
    errors = []
    parse_data = copy.deepcopy(data)
    parse_data = parse_data[parse_data.point_text != ""]
    for index, row in parse_data.iterrows():
        if pd.notnull(parse_data.loc[index, 'point_text']):
            try:
                p = GeoPoint.from_string(row['point_text'])
                row['lat'] = p.latitude
                row['lon'] = p.longitude
                row['string'] = p.format_unicode()
            except Exception as e:
                errors.append((index, e))
    if errors:
        send = Warning()
        send.indexes = errors
        raise send
    return parse_data

def make_shape(data, *args, **kwargs):
    now = datetime.now()
    points = copy.deepcopy(data)
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    name = kwargs.get('name', dt_string)

    if name == "":
        name = dt_string
    
    type = kwargs.get('type', "Points")
    linecolor = kwargs.get('linecolor', '#000000')
    fillcolor = kwargs.get('fillColor', '#000000')
    opacity = kwargs.get('opacity', 50)
    radius = kwargs.get('radius', "15")
    icon = kwargs.get('icon', 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png')
    if type == "Polygon":
        start = points.head(1)
        points = pd.concat([points, start])

    new_shape = {
        'name':name, 
        'type':type,
        'linecolor':linecolor,
        'fillcolor':fillcolor,
        'icon':icon,
        'points':points,
        'radius':radius,
        'opacity' : opacity,
    }
    return new_shape
   

def draw_shapes(shapes_master, *args, **kwargs):

        temp = kwargs.get('temp', None)
        shapes = copy.deepcopy(shapes_master)
        if temp:
            shapes.append(temp)
        if shapes:
            fig = go.Figure()
            for shape in shapes:
                data = shape['points']
                match shape['type']:
                    case "Points":
                        mode = "text"
                    case "Line":
                        mode = "lines"
                    case "Polygon":
                        mode = "lines"
                        #start = data.head(1)
                        #data = pd.concat([data, start])
                        
                    case "Circle":
                        mode = "lines"
    
                trace = go.Scatter(
                    x=data['lon'].to_list(), 
                    y=data['lat'].to_list(), 
                    text = data['name'].to_list(), 
                    mode=mode, 
                    line_color=shape['linecolor'],
                    textposition='top right',
                    marker_color= shape['linecolor'],
                    opacity=(shape['opacity']/100),
                    textfont=dict(
                        size=18,
                        color=shape['linecolor']
                    
                    ),
                    name = shape['name']
                )
                fig.add_trace(trace)
                if shape['type'] == "Points":
                    for i, x in enumerate(data['lon']):
                        fig.add_layout_image(
                                dict(
                                    source=shape['icon'],
                                    xref="x",
                                    yref="y",
                                    x=x,
                                    y=data['lat'].iloc[i],
                                    sizex=0.1,
                                    sizey=0.1,
                                    xanchor="center",
                                    yanchor="middle",
                                    layer='above',
                                    sizing='contain',
                                    
                                    opacity=0.5,
                                )
                        )
            
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
            fig.update_layout(
                #width=kwargs.get("size"),
                #height=kwargs.get("size"),
                autosize=True,
                margin=dict(l=10, r=10, t=10, b=10),
                
            )
            return fig

class Collection():
    def __init__(self,*args, **kwargs):
        self._data = {
            'points': None,
            'shapes' : [],
        }
        self._points = kwargs.get('points', None)
        self.points = None






        self._dataFrame = False
        self._shapePoints = []
        self._shapePolygon = []
        self._shapeCircles = []
        self._shapeLine = []
        self.icon = False
        self.type = False
        self.lat = False
        self.lon = False
        self.pointsText = False






    def new_data(self):
        return None


    def dataFrameInit(self):
        self._dataFrame = pd.DataFrame(
        {
            "name": "",
            "pointsText": self.pointsText,
            "lat": self.lat,
            "lon": self.lon,
            "radius" : "",
        }
        
        )
        


    @property
    def dataFrame(self):
        return self._dataFrame
        
    @dataFrame.setter
    def dataFrame(self, newDataFrame):
        self._dataFrame = newDataFrame
        







    def stringToObject(self, string):
        errors = []
        pointsText = []
        lat = []
        lon = []
        lines = string.split("\n")
        for i, line in enumerate(lines):
            latP, lonP , pointText,  error = self.stringToPoint(line)
            lat.append(latP)
            lon.append(lonP)
            pointsText.append(pointText)
            
            if error:
                errors.append ("An error occurred on line "+ str(i) + ": " + str(line))

        points = pd.DataFrame()
        self.pointsText = pointsText
        self.dataFrameInit()
        return errors


        #returnDataframe = pd.df2 = pd.DataFrame(
        #{
        #    "Name": names,
        #    "Point": points,
        #    "Decimal Point": decimalPoints,
        #    "Text Point": textPoints,
        #    "Icon": "",
        #    "Radius" : "", 
        #}

    def stringToPoint(self, point):
        message = False
        error = False
        try: 
                p = GeoPoint.from_string(point)
                
                if p == None:
                    raise Exception("None returned") 
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            #message += ("Error at line "+str(i)+" :")
            message = template.format(type(ex).__name__, ex.args)
            #message += "\n\n"
            #print ("\n\n",message, "\n\n")
            
            return message, message,  True
        else:
            return p.latitude , p.longitude, p.format_unicode() , False
            #point = p.format_unicode()
            #decimalPoints.append(decimalPoint)
            #pointsDecimal.append(point)
    
    @property
    def Points(self):
        points = []
        for point in self.points:
            points.append(Point(point))
        return points

                
    def trace(self, *args, **kwargs):
        dataFrame = kwargs.get('dataframe',self._dataFrame)
        #print(self._dataFrame['pointsDec'].to_list())   
        trace = go.Scatter(
            x=dataFrame['lon'].to_list(), 
            y=dataFrame['lat'].to_list(), 
            text = dataFrame['name'].to_list(), 
            mode='lines+markers+text', 
            line_color=self.colorLine,
            textposition='top right',
            marker_color='#000000',
            textfont=dict(
                size=18,
                color=self.colorLine
            )
            )

        
        return trace
    
    def table_points(self):
        classType = type(self).__name__
        #radius = kwargs.get('radius',False)
        #name = kwargs.get('name',False)






class CollectionA():
    def __init__(self, data ,*args, **kwargs):
     
        self._data = data
        self.errors = False
        self.points = list(data["Decimal Point"])       
        #data.loc[:, ["Decimal Point"]].values
    
        self.color = "#4287f5"
        self.colorFill = "#0087f5"
    
    @property
    def data(self):
        print("Data retrieved ---------------->\n\n", self._data, "\n\n")
        return self._data

    @data.setter
    def data(self, newData):
        self._data = newData
        print("Data set to  ---------------->\n\n", self._data, "\n\n")
        
    
    @property
    def getScatter(self):
        x1=[]
        y1=[]
 
        for coord in self.points:
            x1.append(coord[1])
            y1.append(coord[0])
        scatter = go.Scatter(x=x1, y=y1,mode='lines+markers', line_color=self.color, marker_color='#000000')
        
        return scatter


    
    
    def table(self):
        classType = type(self).__name__
        #radius = kwargs.get('radius',False)
        #name = kwargs.get('name',False)
        gb = GridOptionsBuilder.from_dataframe(self.data)
        gb.configure_default_column( editable=False)
        #gb.configure_default_column(rowDrag = True, rowDragManaged = True, rowDragEntireRow = True, rowDragMultiRow=True)
        #gb.configure_column('Index', rowDrag = False, rowDragEntireRow = True,editable=True, width = 30)
        gb.configure_column('Name', rowDrag = False, rowDragEntireRow = True,editable=True)
        gb.configure_column('Point', editable=True, hide = True)
        gb.configure_column('Decimal Point', editable=False, hide = True)
        gb.configure_column('Text Point', editable=True)
        gb.configure_column('Icon', hide = True)
        if classType == "ACircle":
            gb.configure_column('Radius', hide=False, editable=True)
        else:
            gb.configure_column('Radius', hide=True, editable=False)

        
        gb.configure_grid_options(domLayout='normal')
        gridOptions = gb.build()
        return_mode_value = DataReturnMode.__members__['AS_INPUT']
        update_mode_value = GridUpdateMode.__members__['VALUE_CHANGED']
      
        return AgGrid(self.data,
                    gridOptions=gridOptions,
                    width='100%',
                    data_return_mode=return_mode_value, 
                    update_mode=update_mode_value,
                    fit_columns_on_grid_load=True ,
                    allow_unsafe_jscode=False,
                    enable_enterprise_modules=False
                    )

            
    def fig(self, *args, **kwargs):
        classType = type(self).__name__
        fig = go.Figure()
        fig.update_yaxes(
            showticklabels=False,
            showgrid=False,
            scaleanchor = "x",
            scaleratio = 1,
            )
        if 'size' in kwargs: 
            fig.update_layout(
            width=kwargs.get("size"),
            height=kwargs.get("size"),
            )

        fig.update_xaxes(showticklabels=False,showgrid=False)
        fig.update_traces(textposition='top center')
        fig.update_layout(
            autosize=False,

            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10)
        )
      
        newShape = self.getScatter
        #if 'size' in kwargs or shape.type == "Circle": 
        if classType == "APoints":
            newShape.mode='markers+text'

            newShape.text = self.data["Name"]
            newShape.textposition="bottom center"
            newShape.textfont=dict(

                size=18,
                color=self.color
            )

        else:
            newShape.mode='lines'
        fig.add_trace(newShape)
        return fig









class ALine(Collection):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data)
        self.poly = LineString(self.points)

class APoints(Collection):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data)
        self.poly = Point(self.points)

class ALine(Collection):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data)
        self.poly = LineString(self.points)

class APolygon(Collection):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data)
        self.poly = Polygon(self.points)

class ACircle(Collection):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data)
        self.radius = data.loc[0]['Radius']
        

        self.point = self.points[0]

        if self.radius:
            self.poly = self.polyCircle(self.point, self.radius)

from pyproj.crs import ProjectedCRS
from pyproj.crs.coordinate_operation import AzumuthalEquidistantConversion




def polyCircle(data, radius):
    lat = data['lat'].head()[0]
    lon = data['lon'].head()[0]



    radius = int(radius) * 1852
    proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')

    # Azimuthal equidistant projection
    aeqd_proj = "+proj=aeqd +R=6371000 +units=m +lat_0={lat} +lon_0={lon}"
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(float(lon), float(lat)).buffer(radius)  # distance in metres

    #st.write(transform(project, buf).exterior.coords[:])
    return transform(project, buf).exterior.coords.xy

           
def polyCirclea(data , radius):
    # Buckingham Palace, London
    #print("coords-------------->",type(coords),"\n\n\n\n\n\n", coords)

    lat = data['lat'].head()
    lon = data['lon'].head()

    #lon, lat = -122.431297, 37.773972 # lon lat for San Francisco
    radius = 100  # in m

    #print("radius-------------->\n\n\n\n\n\n", radius)
    radius = int(radius) * 1852  # radius in meters

    local_azimuthal_projection = "+proj=aeqd +R=6371000 +units=m +lat_0={} +lon_0={}".format(lat, lon)
    wgs84_to_aeqd = partial(
    pyproj.transform,
    pyproj.Proj("+proj=longlat +datum=WGS84 +no_defs"),
    pyproj.Proj(local_azimuthal_projection),
    )
    aeqd_to_wgs84 = partial(
    pyproj.transform,
    pyproj.Proj(local_azimuthal_projection),
    pyproj.Proj("+proj=longlat +datum=WGS84 +no_defs"),
    )
    center = Point(float(lon), float(lat))
    point_transformed = transform(wgs84_to_aeqd, center)
    buffer = point_transformed.buffer(radius)

    # Get the polygon with lat lon coordinates
    circle_poly = transform(aeqd_to_wgs84, buffer)
    return circle_poly.exterior.coords.xy

    local_azimuthal_projection = "+proj=aeqd +R=6371000 +units=m +lat_0={} +lon_0={}".format(lng, lat)
    wgs84_to_aeqd = Transformer.from_proj('+proj=longlat +datum=WGS84 +no_defs',local_azimuthal_projection)
    aeqd_to_wgs84 = Transformer.from_proj(local_azimuthal_projection,'+proj=longlat +datum=WGS84 +no_defs',always_xy = False)
    # Get polygon with lat lon coordinates

    point_transformed = Point(wgs84_to_aeqd.transform(lat, lng))
    buffer = point_transformed.buffer(radius, resolution=32)
    circle = transform(aeqd_to_wgs84.transform, buffer)
    return buffer.exterior.coords.xy
    return list(circle.exterior.coords)
    tcircle = [t[::-1] for t in self.polyPoints]
    self.points = tcircle
    return  Polygon(tcircle)
   
    lat = coords[0][0]
    lng = coords[0][1]
    radius = int(radius) * 1852  # radius in meters
    local_azimuthal_projection = "+proj=aeqd +R=6371000 +units=m +lat_0={} +lon_0={}".format(lat, lng)
    wgs84_to_aeqd = Transformer.from_proj('+proj=longlat +datum=WGS84 +no_defs',local_azimuthal_projection)
    aeqd_to_wgs84 = Transformer.from_proj(local_azimuthal_projection,'+proj=longlat +datum=WGS84 +no_defs',always_xy = False)
    # Get polygon with lat lon coordinates
    point_transformed = Point(wgs84_to_aeqd.transform(lng, lat))
    buffer = point_transformed.buffer(radius, resolution=32)
    circle = transform(aeqd_to_wgs84.transform, buffer)
    self.polyPoints = list(circle.exterior.coords)
    tcircle = [t[::-1] for t in self.polyPoints]
    self.polyPoints = tcircle


        










class ShapeGEn():
    def __init__(self, type, points, sessionVars , *args, **kwargs):
        super().__init__()


     

        self.circleRadius = kwargs.get('circleRadius',False)
        self.circlePoints = kwargs.get('circlePoints',False)
        match self.type:

            case "Point": #points
                self.polyPoints = self.points[0]
                self.poly = Point(self.points[0])

            case "Line": #line
                self.polyPoints = self.points
                self.poly = self.polyLine(self.points)

            case "Polygon": #poly
                self.polyPoints = self.points
                self.poly = self.polyPoly(self.points)

            case "Circle": #circle
            
                self.poly = self.polyCircle(self.points, self.circleRadius)


    def addToEdit(self):
        self.sessionVars["shapeEdit"].append(self)
    

    def kmlState(self):
        #copy(self.kmlCheck)
        if self.kmlCheck == False and self in self.sessionVars["kmlEdit"]:
            self.sessionVars["kmlEdit"].remove(self)
        else:
            self.sessionVars["kmlEdit"].append(self)
    


    @property
    def getScatter(self):
        x1=[]
        y1=[]
 
        for coord in self.polyPoints:
            x1.append(coord[1])
            y1.append(coord[0])
        #if self.type == "Circle" or self.type == "Polygon":
        #    fill = "toself"
        #else:
        #    fill = None
        scatter = go.Scatter(x=x1, y=y1,mode='lines+markers', line_color=self.colorLine, marker_color='#000000')
        
        return scatter
        


    def printCoords(self, coords):
        df = pd.DataFrame(
            coords,
            columns=("Decimal Latitude","Decimal Longitude")
                            )
        with st.expander("ℹ️ - Review decimal coordinates", expanded=False):
            st.dataframe(df)  
        




    def polyCircle(self , coords , radius):
        # Buckingham Palace, London
        lat = coords[0][0]
        lng = coords[0][1]
        radius = int(radius) * 1852  # radius in meters
        local_azimuthal_projection = "+proj=aeqd +R=6371000 +units=m +lat_0={} +lon_0={}".format(lat, lng)
        wgs84_to_aeqd = Transformer.from_proj('+proj=longlat +datum=WGS84 +no_defs',local_azimuthal_projection)
        aeqd_to_wgs84 = Transformer.from_proj(local_azimuthal_projection,'+proj=longlat +datum=WGS84 +no_defs',always_xy = False)
        # Get polygon with lat lon coordinates
        point_transformed = Point(wgs84_to_aeqd.transform(lng, lat))
        buffer = point_transformed.buffer(radius, resolution=32)
        circle = transform(aeqd_to_wgs84.transform, buffer)
        self.polyPoints = list(circle.exterior.coords)
        tcircle = [t[::-1] for t in self.polyPoints]
        self.polyPoints = tcircle
        return  Polygon(tcircle)
        


    def polyLine (self , coords):
        return LineString(coords)

    def polyPoly (self, coords):
        coords.append(coords[0])
        return  Polygon(coords)
            




def operate(shape1,shape2,operator):
    shapes=[]
    error=False
    match operator:
     
        case "Add or Subtract":
            if shape1.poly.intersects(shape2.poly):
                shapes.append(shape1.poly.difference(shape2.poly))
                shapes.append(shape2.poly.difference(shape1.poly))
                shapes.append(shape2.poly.union(shape1.poly))
            else:
                error = "The shapes do not intersect, you can add multiple non-intersecting shapes to the same .kml in the '.kml Composer' tab"

        
        case "Slice":
        
            try:
                buff_line = shape2.poly.buffer(0.001)  #is polygon
                parts = shape1.poly.difference(buff_line)
                for geom in parts.geoms:
                    shapes.append(geom)
            except:
                error = "Your line does not cut the shape you selcted, to slice a shape your line needs to cut the shape in at least two places.  Your selected line and shape should be displayed below"
        


    #return list(shapes.exterior.coords)
    return shapes, error
    