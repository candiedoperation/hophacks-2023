import io
import threading
from tkinter import Image
import cv2
import ee
import inspect
from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import auth
import base64
from PIL import Image

app = Flask(__name__)
CORS(app)

# Initialize Earth Engine
ee.Initialize()

sample_weather = '''
{
    "air_quality": {
        "air_quality": {
            "NO2_column_number_density": 8.841316729092914e-05,
            "O3_column_number_density": 0.12442222100250704,
            "SO2_column_number_density": -3.5792676949686674e-05,
            "CO_column_number_density": 0.03094273342713944
        }
    },
    "weather_quality": {
        "Tair_f_inst": 302.5200500488281
    },
    "water_quality": {
        "nd": null
    },
    "elevation": {
        "elevation": 6.699294066714051
    },
    "Surface_Temp": {
        "LST_Day_1km": 15431.85680379747
    },
    "Precipitation": {
        "precipitation": 0.5368225574493408
    },
    "Climate Data": {
        "dewpoint_2m_temperature": 298.8488464355469,
        "maximum_2m_air_temperature": 304.2912292480469,
        "mean_2m_air_temperature": 301.48565673828125,
        "mean_sea_level_pressure": 100432.5078125,
        "minimum_2m_air_temperature": 299.0939636230469,
        "surface_pressure": 100052.9140625,
        "total_precipitation": 0.3936968445777893,
        "u_component_of_wind_10m": 1.0503805875778198,
        "v_component_of_wind_10m": 2.873635768890381
    },
    "AvgSurfT_inst": {
        "AvgSurfT_inst": 305.7236022949219
    },
    "CanopInt_inst": {
        "CanopInt_inst": 0.19024138152599335
    },
    "ECanop_tavg": {
        "ECanop_tavg": 6.824655055999756
    },
    "ESoil_tavg": {
        "ESoil_tavg": 0
    },
    "Evap_tavg": {
        "Evap_tavg": 2.7300188776280265e-06
    },
    "LWdown_f_tavg": {
        "LWdown_f_tavg": 443.0003662109375
    },
    "PotEvap_tavg": {
        "PotEvap_tavg": 303.99737548828125
    },
    "Psurf_f_inst": {
        "Psurf_f_inst": 100238.2421875
    },
    "Qair_f_inst": {
        "Qair_f_inst": 0.01909104362130165
    },
    "Qg_tavg": {
        "Qg_tavg": 0.4034406244754791
    },
    "SoilMoi0_10cm_inst": {
        "SoilMoi0_10cm_inst": 31.992578506469727
    },
    "SoilMoi100_200cm_inst": {
        "SoilMoi100_200cm_inst": 298.57159423828125
    },
    "Wind_f_inst": {
        "Wind_f_inst": 4.724437713623047
    }
}
'''


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


# Declare as global to modify it in this function
global quality_of_life_metrics
quality_of_life_metrics = {}
lock = threading.Lock()

# Define the Area of Interest (AOI)
global aoi
aoi = def_aoi(19.07283, 72.88261)


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
    with lock:
        quality_of_life_metrics.update(combined_data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return combined_data


def get_WeatherQuality():
    # Weather Quality
    weather_quality = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
                       .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
                       .mean()
                       .select('Tair_f_inst')
                       .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
                       .getInfo())

    with lock:
        quality_of_life_metrics.update(weather_quality)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return weather_quality


def get_WaterQuality():
    # Water Quality
    water_quality = (ee.Image('LANDSAT/LC08/C01/T1_TOA/LC08_044034_20140318')
                     .normalizedDifference(['B3', 'B5'])
                     .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=30, maxPixels=1e9)
                     .getInfo())

    with lock:
        quality_of_life_metrics.update(water_quality)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return water_quality


def get_elev():
    elevation = ee.Image('USGS/SRTMGL1_003').reduceRegion(
        reducer=ee.Reducer.mean(), geometry=aoi, scale=30, maxPixels=1e9).getInfo()

    with lock:
        quality_of_life_metrics.update(elevation)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return elevation


def get_surface_temp():
    surface_temp = (ee.ImageCollection('MODIS/006/MOD11A1')
                    .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
                    .mean()
                    .select('LST_Day_1km')
                    .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=1000, maxPixels=1e9)
                    .getInfo())

    with lock:
        quality_of_life_metrics.update(surface_temp)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
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

    with lock:
        quality_of_life_metrics.update(precipitation)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
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

    with lock:
        quality_of_life_metrics.update(era5_data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return era5_data


def get_AvgSurfT_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['AvgSurfT_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data


def get_Wind_f_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Wind_f_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data


def get_CanopyWatContent_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['CanopInt_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# time-averaged canopy water evaporation


def get_ECanop_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['ECanop_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# time-averaged soil water evaporation


def get_ESoil_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['ESoil_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# time-averaged total evaporation


def get_Evap_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Evap_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# time-averaged downward longwave radiation flux


def get_LWdown_f_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['LWdown_f_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# time-averaged potential evaporation rate


def get_PotEvap_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['PotEvap_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# instantaneous surface air pressure


def get_Psurf_f_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Psurf_f_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# instantaneous specific humidity


def get_Qair_f_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Qair_f_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# time-averaged ground heat flux


def get_Qg_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Qg_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data


# Accumulated surface runoff
def get_Qs_acc():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Qs_acc'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# Accumulated subsurface runoff


def get_Qsb_acc():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Qsb_acc'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# Accumulated snowmelt


def get_Qsm_acc():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Qsm_acc'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# Time-averaged rainfall rate


def get_Rainf_f_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Rainf_f_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# Time-averaged total precipitation rate


def get_Rainf_tavg():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Rainf_tavg'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# Instantaneous root zone soil moisture


def get_RootMoist_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['RootMoist_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data


def get_SoilMoi0_10cm_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['SoilMoi0_10cm_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# Instantaneous soil moisture in the 100-200 cm layer


def get_SoilMoi100_200cm_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['SoilMoi100_200cm_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# Instantaneous soil temperature in the 0-10 cm layer


def get_SoilTMP0_10cm_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['SoilTMP0_10cm_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# Instantaneous soil temperature in the 100-200 cm layer


def get_SoilTMP100_200cm_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['SoilTMP100_200cm_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data

# Instantaneous wind speed


def get_Wind_f_inst():
    data = (ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
            .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
            .mean()
            .select(['Wind_f_inst'])
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
            .getInfo())

    with lock:
        quality_of_life_metrics.update(data)

    print(
        f"Function finished: {inspect.currentframe().f_code.co_name}.")
    return data


# def print_era5_bands(model):
#     sample_image = ee.Image(ee.ImageCollection(model).first())
#     print("Available bands: ", sample_image.bandNames().getInfo())


def collect_metrics():

    # Combine all metrics into a single dictionary
    quality_of_life_metrics = [
        get_AirQuality(),
        get_WeatherQuality(),
        get_WaterQuality(),
        get_elev(),
        get_surface_temp(),
        get_precipitation(),
        get_era5(),
        get_AvgSurfT_inst(),
        get_CanopyWatContent_inst(),
        get_ECanop_tavg(),
        get_ESoil_tavg(),
        get_Evap_tavg(),
        get_LWdown_f_tavg(),
        get_PotEvap_tavg(),
        get_Psurf_f_inst(),
        get_Qair_f_inst(),
        get_Qg_tavg(),
        get_SoilMoi0_10cm_inst(),
        get_SoilMoi100_200cm_inst(),
        get_Wind_f_inst()
    ]

    return quality_of_life_metrics


def main_func(lat, long):
    """Main function."""

    # Create a list of functions you want to run in parallel
    functions_to_run = [
        get_AirQuality, get_WeatherQuality, get_WaterQuality, get_elev,
        get_surface_temp, get_precipitation, get_era5, get_AvgSurfT_inst,
        get_CanopyWatContent_inst, get_ECanop_tavg, get_ESoil_tavg, get_Evap_tavg,
        get_LWdown_f_tavg, get_PotEvap_tavg, get_Psurf_f_inst, get_Qair_f_inst, get_Qg_tavg,
        get_SoilMoi0_10cm_inst, get_SoilMoi100_200cm_inst, get_Wind_f_inst
    ]  # Add more functions as needed

    global aoi
    aoi = def_aoi(lat, long)

    # final_answer = collect_metrics()

    # Create threads
    threads = []
    for func in functions_to_run:
        thread = threading.Thread(target=func)
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print(quality_of_life_metrics)
    return quality_of_life_metrics


@app.route('/')
def lol():
    lat = request.args['lat']
    long = request.args['long']
    # Fall back call
    try:
        b = main_func(float(lat), float(long))
    except Exception as e:
        print(f"An exception occurred: {e}")
        b = sample_weather
    return b


@app.route("/im_size", methods=["POST"])
def process_image():
    try:
        print(1)
        base64_image = request.json['image']
        print(2)
        base64_data = base64_image.split(',')
        print(3)
        img_data = base64.b64decode(base64_data[1])
        print(4)
        image_np = np.frombuffer(img_data, dtype = np.uint8)
        print(5)
        img = cv2.imdecode(image_np, flags = cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print(6)
        img = Image.fromarray(img.astype('uint8'))

        img.show()
        return jsonify({'msg': 'success', 'size': [img.width, img.height]})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'error', 'error': str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
