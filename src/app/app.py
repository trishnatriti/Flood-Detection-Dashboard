import streamlit as st
import geemap.foliumap as gmap
import geemap
import json
import os
import geopandas as gpd
import datetime

from flood.flood import Flood

class App:
    

    def run(self):
        #Page configuration
        st.set_page_config(page_title='Flood', layout='wide')
        st.title("Flood Hazard Mapping")
        
        #Parameter configuration
        st.sidebar.title("Set Parameters")
        base_dir = os.path.dirname(os.path.dirname(__file__))
        shp = "data//India_district_level_shapefile.gpkg"
        shape_path = os.path.join(base_dir,shp)
        print(shape_path)
        gdf = gpd.read_file(shape_path)
        states = ['Select State']+list(gdf["State"].unique())
        today = datetime.datetime.today().date()
        previous_15 = today-(datetime.timedelta(days=15))
        
        #User input
        state = st.sidebar.selectbox("Select the state", states)
        if state != "Select State":
            districts = ['Select District']+list(gdf[gdf['State']==state]['District'].unique())
            district = st.sidebar.selectbox("Select the district", districts)

            if district != "Select District":
                threshold = st.sidebar.number_input("Enter the threshold", min_value = -30, max_value = -12, value = -20)
                flood_start = st.sidebar.date_input("Enter the start date", 
                                                    value = previous_15-(datetime.timedelta(days=1)),
                                                    max_value = previous_15-(datetime.timedelta(days=1)))
                flood_end = st.sidebar.date_input("Enter the end date", value = flood_start+(datetime.timedelta(days=1)),
                                                   max_value = flood_start+(datetime.timedelta(days=10)))
                start_date = flood_start.strftime('%Y-%m-%d')
                end_date = flood_end.strftime('%Y-%m-%d')
                
                #Input Json
                flood_json = {"state": state,
                                "district": district,
                                "threshold": threshold,
                                "start_date": start_date,
                                "end_date": end_date}              
                    

                if st.sidebar.button("RUN"):
                    
                    flood = Flood()
                    flood_map, aoi = flood.get_flood(flood_json)
                    Map = gmap.Map()
                    Map.addLayer(flood_map, {"palette": ["blue"]}, 'Flood')
                    Map.addLayer(aoi, {}, 'Area of Interest')
                    Map.centerObject(aoi)
                    Map.to_streamlit()
                    st.success("✅ Operation Executed.")
