import ee
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import geemap
import json
import datetime
from auth.auth import initialize_gee
import os


class Flood:

    initialize_gee()
    
    def get_flood(self, input_json):
        
        '''
        input: 
              json: syntax for storing and exchanging data

        output:
              a: getting watermask from ESA for the aoi
              b: filtering the gdf for aoi
              c: applying the watermask to aoi
              d: selecting proper dates and applying the threshold for the generation of flood map
        '''

        #function to get watermask from ESA
        def get_watermask(roi):
            am1 = (ee.ImageCollection("ESA/WorldCover/v100")
                   .first()
                   .eq(80)
                   .clip(roi)
                   .selfMask())
            am2 = (ee.ImageCollection("ESA/WorldCover/v200")
                   .first()
                   .eq(80)
                   .clip(roi)
                   .selfMask())
            am = am1.Or(am2)
            return am
        
        # filtering gdf for aoi
        base_dir = os.path.dirname(os.path.dirname(__file__))
        shp_dir = r'data\India_district_level_shapefile.gpkg'
        gdf = gpd.read_file(os.path.join(base_dir,shp_dir))
        gdf = gdf[(gdf["State"] == input_json["state"]) & (gdf["District"] == input_json["district"])]

        aoi_fc = ee.FeatureCollection(json.loads(gdf.to_json()))
        
        s1 = (
            ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(aoi_fc)
        )
        waterMask = get_watermask(aoi_fc)
        non_waterMask = waterMask.unmask(0).eq(0).selfMask()

        before_startdate = (datetime.datetime.strptime(input_json['start_date'], '%Y-%m-%d')\
                           -datetime.timedelta(days=15)).strftime('%Y-%m-%d')
        after_startdate = (datetime.datetime.strptime(input_json['end_date'], '%Y-%m-%d')\
                           +datetime.timedelta(days=15)).strftime('%Y-%m-%d')

        before = (s1.filterDate(before_startdate, input_json['start_date'])
                  .select('VH')
                  .median()
                  .clip(aoi_fc)
                  .updateMask(non_waterMask))
        
        after = (s1.filterDate(input_json['end_date'], after_startdate)
                 .select('VH')
                 .median()
                 .clip(aoi_fc)
                 .updateMask(non_waterMask))
        
        #threshold selection for flood map
        flood = before.gt(input_json['threshold']).And(after.lt(input_json['threshold'])).selfMask()

        return flood, aoi_fc
