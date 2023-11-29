# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 22:01:16 2022

@author: geoadmin
"""

import os
import math
from osgeo import gdal
import numpy as np
import random
import fiona
from shapely.geometry import mapping, shape, LineString, Polygon, Point
from fiona.crs import from_epsg
from PIL import Image

import cv2
import pickle
import matplotlib.pyplot as plt


# add paddings to make the whole map divisible by 128x128 subimages
def add_padding_copy(rasterArray):
    rows,columns,channels = rasterArray.shape
    map_array = []
    newrows = np.ones((64,columns))*255
    newcolumns = np.ones((rows+64,40))*255
    for i in range(len(rasterArray[0][0])):
        image =  rasterArray[:,:,i]    
        image  = np.vstack([image ,newrows])
        image  = np.hstack([image ,newcolumns])
        map_array.append(image)
    map_array = np.array(map_array)  #convert from list to array 
    map_array = np.reshape(map_array, (4864,7040,3))    
    return map_array


def add_padding(rasterArray):
    rows,columns,channels = rasterArray.shape
    newrows = np.ones((64,columns))*255
    newcolumns = np.ones((rows+64,40))*255

    image1 =  rasterArray[:,:,0]    
    image2 =  rasterArray[:,:,1] 
    image3 =  rasterArray[:,:,2] 
    image1  = np.vstack([image1 ,newrows])
    image1  = np.hstack([image1 ,newcolumns])
    image2  = np.vstack([image2 ,newrows])
    image2  = np.hstack([image2 ,newcolumns])
    image3  = np.vstack([image3 ,newrows])
    image3  = np.hstack([image3 ,newcolumns])
    temp = np.array([image1,image2,image3])
    map_array = np.moveaxis(temp, 0, -1)
    # temp = np.transpose(temp)
    # maparray.append(temp)
    
    # map_array.append(image)
    # map_array = np.array(map_array)  #convert from list to array 
    # map_array = np.transpose(temp, (4864,7040,3))    
    return map_array

# clip the map after padding into several 128x128 subimages without changing the order of RGB
# def clip_image_copy(map_array, size):
#     subimage_list = []
#     for i in range(0,len(map_array),size):
#         rows =  map_array[i:i+size,:,:]
#         for j in range(0, len(map_array[0]), size):
#             subimage = rows[:,j:j+size,:]
#             # image = subimage.reshape(3,128,128)
#             # plt.imshow(image[0])
#             # plt.show() 
#             # plt.imshow(image[1])
#             # plt.show() 
#             # plt.imshow(image[2])
#             # plt.show() 

#             img_arr_plt = subimage/255
#             # plt.imshow(img_arr_plt)
#             # plt.show()
#             subimage_list.append(subimage)
#     return subimage_list
            

# clip the map into several 128x128 subimages 
def clip_image(map_array, size):
    subimage_list = []
    for i in range(0,len(map_array),size):
        print(i)
        rows =  map_array[i:i+size,:,:]
        for j in range(0, len(map_array[0]), size):
            image = rows[:,j:j+size,:] #RGB
            # image = subimage.reshape(3,128,128)
            # plt.imshow(image[0])
            # plt.show() 
            # plt.imshow(image[1])
            # plt.show() 
            # plt.imshow(image[2])
            # plt.show() 
            arr1 = image[:,:,0:1]#R
            arr2 = image[:,:,1:2]#G
            arr3 = image[:,:,2:3]#B
            # tempimage = format_array(arr3,arr2,arr1) #RGB to BGR, (128,1,128,3)
            tempimage = format_array(arr3,arr2,arr1) #BGR
            subimage = tempimage.reshape(128,128,3)

            # plt.imshow(subimage)
            # plt.show()
            # img = subimage.astype(np.uint8)
            subimage_list.append(subimage)
    return subimage_list

# combine 3 channel arrays into an image
def format_array(arr1,arr2,arr3):
    maparray = []
    for i in range(0,len(arr1)):
        col1 = arr1[i]
        col2 = arr2[i]
        col3 = arr3[i]
        temp = np.array([col1,col2,col3])
        temp = np.transpose(temp)
        maparray.append(temp)
    maparray = np.array(maparray)
    return maparray
                        
def export_images(images):
    for i in range(len(images)):
        image = images[i]
        image = image.astype(np.uint8)
        im = Image.fromarray(image)
        name = '%04d' % (i+1) 
        path = 'clips/' + name +'.jpg'
        im.save(path)            


filepath = r"sheets/skeleton.tif"
# filepath = r"data/road_data/rgb_TA_161_1940_3bands.tif"
map_arr = cv2.imread(filepath, cv2.IMREAD_COLOR)  #4800x7000x3 in array of uint8
map_arr_copy = np.where(map_arr>0,0,255).astype(np.uint8)
origin_shape = (map_arr.shape[1], map_arr.shape[0])

map_array = add_padding(map_arr_copy).astype(np.uint8) #4800x7000x3 in array of float64

subimage_list = clip_image(map_array, 128)
export_images(subimage_list)



# #acquire coordinates of white points(road sgment)
# road_coordinates = np.argwhere(arr == 0)
# # removed the pixels close to the boundary from the candidate pixels
# filter_pixels = road_coordinates[ (64<road_coordinates[:,0]) & (road_coordinates[:,0]<width-64) & (road_coordinates[:,1]>64) & (road_coordinates[:,1]<height-64)]
# idx = np.random.randint(filter_pixels.shape[0],size = Num)
# #select the final candidates to cut the 128x128 images
# selected_pixels = filter_pixels[idx,:]
# image_list=select_pixels_by_index(arr, selected_pixels)
# export_images(image_list)