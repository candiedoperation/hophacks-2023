# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 01:03:45 2023

@author: Kushal
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 17:37:19 2023

@author: Kushal
"""

import cv2
import requests
import numpy as np
from roboflow import Roboflow
import json
from flask import Flask,request, jsonify
import math
import IPython.display as display
import threading
import ee

app = Flask(__name__)

def latlongToTile(lat, long, zoom):
    n = 2 ** zoom
    latRads = math.radians(lat)
    tileX = n * ((long + 180.0) / 360.0)
    tileY = n * (1.0 - (math.log(math.tan(latRads) + 1.0/math.cos(latRads)) / math.pi)) / 2.0
    return (int(tileX), int(tileY))

def latlongToUrl(lat, long, zoom):
    lat1, long1 = latlongToTile(lat, long, zoom)
    url = "http://mt1.google.com/vt/lyrs=s&x=%d&y=%d&z=%d" % (lat1, long1, zoom)
    response = requests.get(url)
    display.Image(data=response.content)
    return url

def gen(res, lat, long):

    instructions = """
    I will give you the result of the object detection of a region. I want you to give me a description of the actual region based on this data. This should be more than just the details of the detections on the image. Our goal is to help predict where we can help deploy volunteers for maximum efficiency of resources. You must make inferences as these volunteers are remote workers, who cannot help in local affairs. These volunteers are not going to be effective at all during basic labourous tasks, but rather for more intellectual tasks, which can be done remotely.

"""
    prompt = """
    Instructions:
    {instructions}
    
    the coordinates of the place are: 
    lat = {lat}, long = {long}
    
    Here is the Information about the damages :
    {damages}


    """.format( damages = res, lat = lat, long = long, instructions=instructions)
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-3.5-turbo-16k",
        "messages": [
                {"role": "user", "content": prompt},
    
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()
    
    summary = result['choices'][0]['message']['content']

    return summary


# Initialize Earth Engine
ee.Initialize()


def def_aoi(latitude, longitude, d_lat=0.01, d_lon=0.01):
    """Creates an AOI for the analysis."""
    aoi = ee.Geometry.Polygon([
        [longitude - d_lon, latitude - d_lat],
        [longitude + d_lon, latitude - d_lat],
        [longitude + d_lon, latitude + d_lat],
        [longitude - d_lon, latitude + d_lat],
        [longitude - d_lon, latitude - d_lat]
    ])
    return aoi


# Define the Area of Interest (AOI)
aoi = def_aoi(28.657905, 77.210369)


def get_AirQuality():
    # Air Quality
    no2 = (ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2')
           .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
           .mean()
           .select('NO2_column_number_density')
           .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=1000, maxPixels=1e9)
           .getInfo())

    o3 = (ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_O3").filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
          .mean()
          .select('O3_column_number_density')
          .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=1000, maxPixels=1e9)
          .getInfo())

    so2 = (ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_SO2")
           .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
           .mean()
           .select('SO2_column_number_density')
           .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=1000, maxPixels=1e9)
           .getInfo())

    co = (ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_CO")
          .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
          .mean()
          .select('CO_column_number_density')
          .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=1000, maxPixels=1e9)
          .getInfo())

    # Combine them into a single dictionary
    combined_data = {
        'air_quality': {
            **no2,
            **o3,
            **so2,
            **co
        }
    }

    return combined_data


def get_WeatherQuality():
    # Weather Quality
    weather_quality = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
                       .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
                       .mean()
                       .select('Tair_f_inst')
                       .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
                       .getInfo())
    return weather_quality


def get_WaterQuality():
    # Water Quality
    water_quality = (ee.Image('LANDSAT/LC08/C01/T1_TOA/LC08_044034_20140318')
                     .normalizedDifference(['B3', 'B5'])
                     .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=30, maxPixels=1e9)
                     .getInfo())
    return water_quality


def get_elev():
    elevation = ee.Image('USGS/SRTMGL1_003').reduceRegion(
        reducer=ee.Reducer.mean(), geometry=aoi, scale=30, maxPixels=1e9).getInfo()

    return elevation


def get_surface_temp():
    surface_temp = (ee.ImageCollection('MODIS/006/MOD11A1')
                    .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
                    .mean()
                    .select('LST_Day_1km')
                    .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=1000, maxPixels=1e9)
                    .getInfo())
    return surface_temp


def get_precipitation():
    precipitation = (ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V06')
                     # Filter by date
                     .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
                     .mean()  # Take the mean over the time period
                     # Select the 'precipitation' band
                     .select('precipitation')
                     .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
                     .getInfo())  # Get the mean precipitation in the AOI
    return precipitation


def get_era5():
    era5_data = (ee.ImageCollection('ECMWF/ERA5/MONTHLY')
                 # Filter by date
                 .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
                 .mean()  # Take the mean over the time period
                 # Select specific bands
                 .select(['mean_2m_air_temperature', 'minimum_2m_air_temperature', 'maximum_2m_air_temperature', 'dewpoint_2m_temperature', 'total_precipitation', 'surface_pressure', 'mean_sea_level_pressure', 'u_component_of_wind_10m', 'v_component_of_wind_10m'])
                 .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
                 .getInfo())  # Get the average values within the AOI
    return era5_data


def get_AvgSurfT_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['AvgSurfT_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data


def get_Wind_f_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Wind_f_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data


def get_CanopyWatContent_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['CanopInt_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# time-averaged canopy water evaporation


def get_ECanop_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['ECanop_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# time-averaged soil water evaporation


def get_ESoil_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['ESoil_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# time-averaged total evaporation


def get_Evap_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Evap_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# time-averaged downward longwave radiation flux


def get_LWdown_f_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['LWdown_f_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# time-averaged potential evaporation rate


def get_PotEvap_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['PotEvap_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# instantaneous surface air pressure


def get_Psurf_f_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Psurf_f_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# instantaneous specific humidity


def get_Qair_f_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Qair_f_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# time-averaged ground heat flux


def get_Qg_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Qg_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data


# Accumulated surface runoff
def get_Qs_acc():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Qs_acc'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# Accumulated subsurface runoff


def get_Qsb_acc():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Qsb_acc'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# Accumulated snowmelt


def get_Qsm_acc():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Qsm_acc'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# Time-averaged rainfall rate


def get_Rainf_f_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Rainf_f_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# Time-averaged total precipitation rate


def get_Rainf_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Rainf_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# Instantaneous root zone soil moisture


def get_RootMoist_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['RootMoist_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data


def get_SoilMoi0_10cm_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['SoilMoi0_10cm_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# Instantaneous soil moisture in the 100-200 cm layer


def get_SoilMoi100_200cm_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['SoilMoi100_200cm_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# Instantaneous soil temperature in the 0-10 cm layer


def get_SoilTMP0_10cm_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['SoilTMP0_10cm_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# Instantaneous soil temperature in the 100-200 cm layer


def get_SoilTMP100_200cm_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['SoilTMP100_200cm_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data

# Instantaneous wind speed


def get_Wind_f_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Wind_f_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())
    return data


def print_era5_bands(model):
    sample_image = ee.Image(ee.ImageCollection(model).first())
    print("Available bands: ", sample_image.bandNames().getInfo())


def collect_metrics():
    global quality_of_life_metrics  # Declare as global to modify it in this function

    # Combine all metrics into a single dictionary
    quality_of_life_metrics = {
        'air_quality': get_AirQuality(),
        'weather_quality': get_WeatherQuality(),
        'water_quality': get_WaterQuality(),
        'elevation': get_elev(),
        'Surface_Temp': get_surface_temp(),
        'Precipitation': get_precipitation(),
        'Climate Data': get_era5(),
        'AvgSurfT_inst': get_AvgSurfT_inst(),
        'CanopInt_inst': get_CanopyWatContent_inst(),
        'ECanop_tavg': get_ECanop_tavg(),
        'ESoil_tavg': get_ESoil_tavg(),
        'Evap_tavg': get_Evap_tavg(),
        'LWdown_f_tavg': get_LWdown_f_tavg(),
        'PotEvap_tavg': get_PotEvap_tavg(),
        'Psurf_f_inst': get_Psurf_f_inst(),
        'Qair_f_inst': get_Qair_f_inst(),
        'Qg_tavg': get_Qg_tavg(),
        'SoilMoi0_10cm_inst': get_SoilMoi0_10cm_inst(),
        'SoilMoi100_200cm_inst': get_SoilMoi100_200cm_inst(),
        'SoilTMP0_10cm_inst': get_SoilTMP0_10cm_inst(),
        'SoilTMP100_200cm_inst': get_SoilTMP100_200cm_inst(),
        'Wind_f_inst': get_Wind_f_inst()
    }


# Create a list of functions you want to run in parallel
functions_to_run = [get_AirQuality, get_WeatherQuality, get_WaterQuality, get_elev,
                    get_surface_temp, get_precipitation, get_era5]  # Add more functions as needed

# Create an empty dictionary to hold the results
def weather_main():
    quality_of_life_metrics = {}
    
    collect_metrics()
    
    # Create threads
    threads = []
    for func in functions_to_run:
        thread = threading.Thread(target=func)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    return quality_of_life_metrics

def vision(image_file, lat, long):
    
    # Define a list of models and model names
    models = [
        {"project_name": "urban-infrastructure-assessment", "version": 4, "name": "Model 1"},
        {"project_name": "dota-aerial-images", "version": 1, "name": "Model 2"},
        {"project_name": "ky-wd2tz", "version": 2, "name": "Model 4"},
        {"project_name": "drone-qzhad", "version": 3, "name": "Model 3"},
    ]
    
    cv_visions = []
    
    # Iterate through the models and display predictions for each model
    for model_info in models:
        project = rf.workspace().project(model_info["project_name"])
        model = project.version(model_info["version"]).model
        x = model.predict(image_file, hosted=True).json()
        p = x['predictions']
        for i in p:
            if i['confidence'] > 0.5:
                cv_visions.append(i)
                
    
    print(cv_visions)
    print(len(cv_visions))
    m = gen(cv_visions, lat, long)

    print(m)
    return m

@app.route('/req')
def lol():
    lat = request.args['lat']
    long = request.args['long']
    return jsonify(vision(latlongToUrl(float(lat),float(long),17), lat, long))


@app.route('/test')
def hehe():
    return jsonify("Hehe lol")

if __name__ == "__main__":
    rf = Roboflow(api_key="7ZBY6Mq7nyCsWG8IdbZC")
    
    app.run(host='0.0.0.0', port=5000)

