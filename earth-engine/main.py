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
aoi = def_aoi(27.9881, 86.9250)


def tifftopng(file):
    with rasterio.open(file) as src:
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


def get_elev():
    elevation = ee.Image('USGS/SRTMGL1_003').reduceRegion(
        reducer=ee.Reducer.mean(), geometry=aoi, scale=30, maxPixels=1e9).getInfo()

    return elevation


def get_surface_temp():
    surface_temp = (ee.ImageCollection('MODIS/006/MOD11A1')
                    .filterDate(ee.Date('2020-01-01'), ee.Date('2020-12-31'))
                    .mean()
                    .select('LST_Day_1km')
                    .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=1000, maxPixels=1e9)
                    .getInfo())
    return surface_temp


def get_precipitation():
    precipitation = (ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V06')
                     # Filter by date
                     .filterDate(ee.Date('2020-01-01'), ee.Date('2020-12-31'))
                     .mean()  # Take the mean over the time period
                     # Select the 'precipitation' band
                     .select('precipitation')
                     .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
                     .getInfo())  # Get the mean precipitation in the AOI
    return precipitation


def get_era5():
    era5_data = (ee.ImageCollection('ECMWF/ERA5/MONTHLY')
                 # Filter by date
                 .filterDate(ee.Date('2020-01-01'), ee.Date('2020-12-31'))
                 .mean()  # Take the mean over the time period
                 # Select specific bands
                 .select(['mean_2m_air_temperature', 'minimum_2m_air_temperature', 'maximum_2m_air_temperature', 'dewpoint_2m_temperature', 'total_precipitation', 'surface_pressure', 'mean_sea_level_pressure', 'u_component_of_wind_10m', 'v_component_of_wind_10m'])
                 .reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10000, maxPixels=1e9)
                 .getInfo())  # Get the average values within the AOI
    return era5_data


def print_era5_bands():
    sample_image = ee.Image(ee.ImageCollection('ECMWF/ERA5/MONTHLY').first())
    print("Available bands: ", sample_image.bandNames().getInfo())


# Combine all metrics into a single dictionary
quality_of_life_metrics = {
    'air_quality': get_AirQuality(),
    'weather_quality': get_WeatherQuality(),
    'water_quality': get_WaterQuality(),
    'elevation': get_elev(),
    'Surface_Temp': get_surface_temp(),
    'Precipitation': get_precipitation(),
    'Climate Data': get_era5()
}

# Save as a JSON file
with open('quality_of_life_metrics.json', 'w') as f:
    json.dump(quality_of_life_metrics, f, indent=4)

print("Data saved as quality_of_life_metrics.json")
