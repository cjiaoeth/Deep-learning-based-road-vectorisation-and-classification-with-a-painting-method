# -*- coding: utf-8 -*-
"""
Created on Sun Jul 24 14:48:18 2022

@author: geoadmin
"""

import os
import pandas as pd
import pickle
import numpy as np
import cv2
import matplotlib.pyplot as plt
import math
from scipy.spatial import distance
from shapely.geometry import LineString, mapping
import fiona
import sys

width = 128
resolution = 1.25
top = 272000
left = 620000
right = 628750
bottom = 266000

# transform the circle center coordinates from image coord system to normal system
def transform_coord(xvalues,yvalues): # to normal system?
    x_values = []
    y_values = []
    for i in range(len(xvalues)):
        x = xvalues[i]
        y = width - yvalues[i]
        x_values.append(x)
        y_values.append(y)
    return x_values, y_values

#transform the point coordinates in each 128x128 image to real spatial coordinates in historical map
# xvalues and yvalues are the x and y values of each point on the image. row and col are the location of the image on the map
def imagecord_to_realcord(xvalues,yvalues,row,col, top, left):

    x_zero = left + 128*col*resolution
    y_zero = top - 128*(row+1)*resolution
    newx = [x*resolution+x_zero for x in xvalues]
    newy = [y*resolution+y_zero for y in yvalues]
    return newx,newy

def points_in_shape(qualified_coords_pairs, top, left):
    x_list = []
    y_list = []
    for i in range(len(qualified_coords_pairs)):
        
        remainder = i % 55 #corresponds to the column index
        row_number = int(i/55) #correspond to the row index
        pairs = qualified_coords_pairs[i]
        
        for j in range(len(pairs)):
            start = pairs[j][0]
            end = pairs[j][1]
            xvalues = [start[0], end[0]]
            yvalues = [start[1], end[1]]
            x_values, y_values = transform_coord(xvalues,yvalues)
            newx,newy = imagecord_to_realcord(x_values,y_values,row_number,remainder, top, left)
            # newx,newy = imagecord_to_realcord(x_values, y_values,0,9, top, left)
            x_list.append(newx)
            y_list.append(newy)
    return x_list,y_list
        
def list_road_class(list_class):
    roadclass = []
    for i in range(len(list_class)):
        temp = list_class[i]
        for j in range(len(temp)):
            rclass = temp[j]
            roadclass.append(rclass)
    return roadclass
                
                

# #generate lines from points per image
def points_to_lines(x_list,y_list):
    linestrings = []
    for i in range(len(x_list)):
        x = x_list[i]
        y = y_list[i]
        lineStringObj = LineString( [[x[j], y[j]] for j in range(0,len(x))] )
        linestrings.append(lineStringObj)
    return linestrings
  

        
def generate_lines(linestrings,roadclass):
    schema = {
        'geometry': "LineString",
        'properties': {"class": "str"},
    }
    
    
    roads_path = "roads_1.5.shp"

    
    with fiona.open(roads_path, 'w', 'ESRI Shapefile', schema) as c:
        for i in range(len(linestrings)):
            linestring = linestrings[i]
            rclass = roadclass[i]
            c.write({"properties":{"class": str(rclass)}, "geometry": mapping(linestring)})                     
                  
if __name__ == '__main__':
    qualified_coords_pairs = pickle.load(open('qualified_coords_pairs_1.5.pkl','rb'))
    list_class = pickle.load(open('road_class_1.5.pkl','rb'))
    x_list, y_list = points_in_shape(qualified_coords_pairs, top, left)
    list_linestrins = points_to_lines(x_list, y_list)
    roadclass = list_road_class(list_class)
    generate_lines(list_linestrins, roadclass)