'''The scripts create a mask layer for deep learning. 
params = raster, vecter  
return = mask and corresponding raw image tile. 

Created by Maxwell Owusu, 2022
'''

# Import libraries
from osgeo import gdal, ogr
from glob import glob
import fiona
from subprocess import Popen
import geopandas as gpd
import rasterio
import numpy as np
import os



def PolyTiles(input_shp, output_shp, prefix=None):
    ''''
    Function for extracting polygon tiles
    params: input_shp = shapefile or geojson, prefix is the prefix to save shape
    output: Shapefiles
    '''
    with fiona.open (input_shp) as dst_in:
        for index, feature in enumerate(dst_in):
            with fiona.open(f'{output_shp}/{prefix}_area{index}.shp', 'w', **dst_in.meta) as dst_out:
                dst_out.write(feature)
    return None

def TiffToVRT(In_Raster_list, Outfile, outputSRS=None):
    '''
    Function for mosiacing tiff into VRT
    params: list of raster files , output spatial reference system
    output: VRT
    '''
    vrt_options = gdal.BuildVRTOptions(outputSRS=outputSRS)
    vrt = gdal.BuildVRT(Outfile, In_Raster_list, options=vrt_options)
    vrt = None

    return None

def read_image(dir):
    """This function read raster image, convert to array and get the geoprojection"""
    img = gdal.Open(os.path.join(dir))
    img_arr = img.ReadAsArray()
    img_gt = img.GetGeoTransform()
    img_georef = img.GetProjectionRef()
    nbands = img_arr.shape[0]
    height = img_arr.shape[1]
    width = img_arr.shape[2]
    return [img_arr, img_gt, img_georef, width, height]

# Clip polygons into Tiles
def ClipVector(in_vector, clip, outfile, prefix=None):
    ''' This functon clip vector '''
    indata = gpd.read_file(in_vector)
    polygons = sorted(glob(clip))
    # print(polygons)
    # num = 0
    for polygon in polygons:
        clip_data = gpd.read_file(polygon)
        clip = gpd.clip(indata, clip_data) # clip function
        # set outfile name
        head, tail = os.path.split(polygon)
        name=tail[:-4]
        clip.to_file(f'{outfile}/{name}.shp', driver='ESRI Shapefile')
    return None