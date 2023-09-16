import ee
import json
import rasterio
from rasterio.enums import Resampling
import urllib.request


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
aoi = def_aoi()


with rasterio.open('input_file.tif') as src:
    data = src.read(
        out_shape=(src.count, int(src.height), int(src.width)),
        resampling=Resampling.bilinear
    )
    transform = src.transform

with rasterio.open('output_file.png', 'w', driver='PNG', height=data.shape[1], width=data.shape[2], count=src.count, dtype=data.dtype) as dst:
    dst.write(data)

def get_image():
    """Get an Earth Engine Image object from GEE."""
    # Select an image (In this example, a Landsat 8 image is used)
    image = (ee.ImageCollection('LANDSAT/LC08/C01/T1')
             .filterBounds(aoi)
             .filterDate(ee.Date('2020-01-01'), ee.Date('2020-12-31'))
             .sort('CLOUD_COVER')
             .first())

    # Specify the image bands and visualization parameters
    bands = ['B4', 'B3', 'B2']  # These are the RGB bands for Landsat 8
    visualization_parameters = {
        'bands': bands,
        'min': 0,
        'max': 3000,
        'region': aoi.getInfo()['coordinates']
    }

    # Generate a URL for the image
    url = image.getThumbURL(visualization_parameters)

    # Download the image as a PNG
    urllib.request.urlretrieve(url, "my_image.png")


def get_AirQuality():
    # Air Quality
    air_quality = (ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2')
                   .filterDate(ee.Date('2020-06-01'), ee.Date('2020-06-30'))
                   .mean()
                   .select('NO2_column_number_density')
                   .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=1000, maxPixels=1e9)
                   .getInfo())

    return air_quality


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


# Combine all metrics into a single dictionary
quality_of_life_metrics = {
    'air_quality': get_AirQuality(),
    'weather_quality': get_WeatherQuality(),
    'water_quality': get_WaterQuality()
}



# Save as a JSON file
with open('quality_of_life_metrics.json', 'w') as f:
    json.dump(quality_of_life_metrics, f, indent=4)

print("Data saved as quality_of_life_metrics.json")
