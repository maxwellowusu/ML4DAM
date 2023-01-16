'''The scripts create a mask layer for deep learning. 
params = raster, vecter  
return = mask and corresponding raw image tile. 

Created by Maxwell Owusu, 2022
'''


#%%
# Import libraries 
from osgeo import gdal, ogr
from glob import glob
import fiona
from subprocess import Popen
import geopandas as gpd
import rasterio
from rasterio import features
import numpy as np
import os
import matplotlib.pyplot as plt

from dataset_preparation import utils_funcs


#--------------- Raster processing ---------------

#%%
# STEP 1
# # Chop polygons into tiles for clipping 

input_shp = 'C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/nai_SHP/Nairobi_Tiles_Polygon_NoIS.shp'
output_shp = 'C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/temp/ClipPolygon/'
prefix = 'nai'
utils_funcs.PolyTiles(input_shp, output_shp, prefix)


# %%

#--------------- Raster processing ---------------
# STEP 2  -  Convert raster to VRT

# Get list of tif files
# Path for image list
# FPATH = '/media/owusu/Extreme SSD/gim_22/nairobi/'
files = sorted(glob(f'C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/nai_contextual_features_2022/*/*.tif'))

# Remove unwanted tif.
# files.remove('/media/owusu/Extreme SSD/gim_22/nairobi/KE_Nairobi_19Q2_V0_BROWSE.tif')

# convert to VRT Reproject to CRS (ignore reprojection if same CRS for vector)

In_Raster_list = files
# outputSRS = 'EPSG:4326'
Outfile = f'C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/spfea.vrt'
utils_funcs.TiffToVRT(In_Raster_list, Outfile,)

# %%
# STEP 3
# Clip raster using polygon Tiles
polygons = sorted(glob('C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/temp/ClipPolygon/*.shp'))
VRT = f'C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/spfea.vrt'
outfile = 'C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/spfea'
# print(polygons)

for polygon in polygons:
    # print(polygon)
    feat = fiona.open(polygon, 'r')
    # add output file name
    head, tail = os.path.split(polygon)
    name=tail[:-4]
    # print(name)
    command = f'gdalwarp -dstnodata -9999 -ts 95 95 -cutline {polygon} -crop_to_cutline -of Gtiff {VRT} "{outfile}/{name}.tif"'
    # command = f'gdalwarp -dstnodata -9999 -cutline {polygon} -crop_to_cutline -of Gtiff {VRT} "{outfile}/{name}.tif"'

    Popen(command, shell=True)

# %%
# STEP 4
# check for constant height and width

files = sorted(glob("C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/final/spfea/*.tif"))
num = 0
for raster in files:
    # print(reference_raster)
    img = utils_funcs.read_image(raster)
    width = img[3]
    height = img[4]
    num += 1
    print(num, width, height)

# --------------- Vector processing ---------------
# STEP 1 Clip polygons into Tiles 


# %%
# Clip polygons into Tiles 

polygons = 'C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/temp/ClipPolygon/*.shp'
input_shp = 'C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/nai_SHP/Nairobi_Tiles_Clip.shp'
outfile = 'C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/temp/IS_Tiles'
prefix = 'Nai'

utils_funcs.ClipVector(in_vector=input_shp, clip=polygons, outfile=outfile, prefix='nai')

# %%
# Step 2 Convert polygon inot raster 

# polygons = sorted(glob('/home/owusu/Documents/AI4IS/data/Nairobi/temp/IS_Tiles/*.shp'))
# RasterTiles = sorted(glob("/home/owusu/Documents/AI4IS/data/Nairobi/final/raw_image/*.tif"))
# output_fp = '/home/owusu/Documents/AI4IS/data/Nairobi/final/labels/'
# # names=[]
# for polygon in polygons:
#     # print(polygon)
#     feat = fiona.open(polygon, 'r')
#     # add output file name
#     head, tail = os.path.split(polygon)
#     name=tail[:-4]
#     # print(name)
#     for raster in RasterTiles:
#         # print(reference_raster)
#         img = utils_funcs.read_image(raster)
#         width = img[3]
#         height = img[4]

#     command = f'gdal_rasterize -a "class_id" -ts {width} {height} -a_nodata -9999 -ot Float32 -of GTiff {polygon} "{output_fp}{name}.tif"'
#     # print (command)
#     Popen (command, shell=True)
# %%

polygons = sorted(glob('C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/temp/IS_Tiles/*.shp'))
RasterTiles = sorted(glob("C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/final/spfea/*.tif"))
outfile = 'C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/final/mask/'

# zip polygon and raster in to a list of tuple 
shp_rast = zip (polygons, RasterTiles)
lst = list(shp_rast)

def rasterize_me(in_shp, in_raster, outfile):
    # read shapfile 
    for i in lst:
        df = gpd.read_file(i[0])
        # add output file name
        head, tail = os.path.split(i[0])
        name=tail[:-4]
    # read raster
        with rasterio.open(i[1], mode="r") as src:
            out_arr = src.read(1)
            out_profile = src.profile.copy()
            out_profile.update(count=1,
                            nodata=-9999,
                            dtype='float32',
                            width=src.width,
                            height=src.height,
                            crs=src.crs)
            dst_height = src.height
            dst_width = src.width
            shapes = ((geom,value) for geom, value in zip(df.geometry, df.CID))
            # print(shapes)
            burned = features.rasterize(shapes=shapes, out_shape=(dst_height, dst_width),fill=0, transform=src.transform)
            plt.imshow(burned) 

        # open in 'write' mode, unpack profile info to dst
        with rasterio.open(f'{outfile}{name}.tif',
                        'w', **out_profile) as dst:
            dst.write_band(1, burned)

# polygons = sorted(glob('/home/owusu/Documents/AI4IS/data/Nairobi/temp/IS_Tiles/*.shp'))
# RasterTiles = sorted(glob("/home/owusu/Documents/AI4IS/data/Nairobi/final/raw_image1/*.tif"))
# outfile = '/home/owusu/Documents/AI4IS/data/Nairobi/final/mask_image1/'

polygons = sorted(glob('C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/temp/IS_Tiles/*.shp'))
RasterTiles = sorted(glob("C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/final/spfea/*.tif"))
outfile = 'C:/Users/mowus/Documents/GWU/gwu_work/ML4DAM/data/nairobi/final/mask/'

rasterize_me(in_shp=polygons, in_raster=RasterTiles, outfile=outfile)
# %%
