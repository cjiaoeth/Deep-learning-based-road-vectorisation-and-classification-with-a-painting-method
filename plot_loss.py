# -*- coding: utf-8 -*-
"""
Created on Sun Jul 10 13:04:11 2022

@author: geoadmin
"""

import os
import cv2
import numpy as np
import draw_lines as dl
from osgeo import gdal
import pickle
import math
import matplotlib.pyplot as plt

os.system('mkdir output')
# os.system('mkdir decomposed')

# def filter_coordinates(list_black_layer):
#     '''
#     Filter the coordinates based on the black layer. The coordinates of black pixels will be kept.

#     Parameters
#     ----------
#     list_black_layer : list
#         the list of black layers. each black layer correspond to one 128x128 map.

#     Returns
#     -------
#     coordinates : list
#         The list of coordinates.

#     '''
#     coordinates = []
#     for i in range(len(list_black_layer)):
#         black_layer = list_black_layer[i]
#         blcaklayer_arr = np.moveaxis(black_layer, 2, 0)
#         thres_arr = np.where(blcaklayer_arr[0] ==0, 1, 0)
#         # thres_arr2 = np.where(blcaklayer_arr < 255, 1, 0)
#         # thres_arr3 = np.where(blcaklayer_arr < 255, 1, 0)
#         # thres_arr = thres_arr1 + thres_arr2 + thres_arr3
#         indices_0 = np.argwhere(thres_arr>0)
#         coordinates.append(indices_0)

#     return coordinates

# def filter_coordinates_1channel(list_black_layer):
#     '''
#     Filter the coordinates based on the black layer. The coordinates of black pixels will be kept.
    
#     The input is tif (1 channel)

#     Parameters
#     ----------
#     list_black_layer : list
#         the list of black layers. each black layer correspond to one 128x128 map.

#     Returns
#     -------
#     coordinates : list
#         The list of coordinates.

#     '''
#     coordinates = []
#     for i in range(len(list_black_layer)):
#         black_layer = list_black_layer[i]
#         thres_arr = np.where(black_layer ==0, 1, 0)
#         indices_0 = np.argwhere(thres_arr>0)
#         coordinates.append(indices_0)

#     return coordinates


def cancel_out(sfmap,img_canvas):
    '''
    Cancel the pixels based on the drawn lines. The corresponding pixels will be marked as white

    Parameters
    ----------
    sfmap : TYPE
        DESCRIPTION.
    img_canvas : TYPE
        DESCRIPTION.

    Returns
    -------
    arr_sfmap : TYPE
        DESCRIPTION.

    '''
    sfmap_copy = sfmap.copy()
    arr_sfmap_copy = np.moveaxis(sfmap_copy, 2, 0)
    canceled_coordinates = np.argwhere(img_canvas == 0)
    filtered_canceled_coordinates = canceled_coordinates[canceled_coordinates[:,2]==0]
    arr_sfmap_copy[0][filtered_canceled_coordinates[:,0],filtered_canceled_coordinates[:,1]] = 255
    arr_sfmap_copy[1][filtered_canceled_coordinates[:,0],filtered_canceled_coordinates[:,1]] = 255
    arr_sfmap_copy[2][filtered_canceled_coordinates[:,0],filtered_canceled_coordinates[:,1]] = 255
    
    arr_sfmap = np.moveaxis(arr_sfmap_copy, 0, -1)
    return arr_sfmap


         

def draw_road_singleline(sfmap, clusters):
    '''
    For each 128x128 historical map, the roads are drawn based on the filtered the coordinates.
    only one symbol is ued 

    Parameters
    ----------
    sfmap : TYPE
        DESCRIPTION.
    coordinates : TYPE
        DESCRIPTION.

    Returns
    -------
    qualified_coords_pairs : TYPE
        DESCRIPTION.

    '''
    
    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255
    sfmap_copy = sfmap.copy()

    best_score = 999
    best_canvas = None
    start_coords = None # will be used to store the quantified paires
    end_coords = None # will be used to store the quantified paires
    qualified_coords_pair = None
    dict_error = {}
    dict_coords = {}
   
    
    if (len(clusters)>=1):
    
        run_times = 0
        counter = 0  

        print("run times", run_times)
        for k in range(len(clusters)):
            coordinates = clusters[k]
            for i in range(len(coordinates)-1):
                start = coordinates[i]
                for j in range(0, len(coordinates)):
                    if i!=j:
                        img_canvas[:,:,:] = 255
                        end = coordinates[j]
             
                        dl.draw_single_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2)
        
                        error = dl.evaluate(img_canvas, sfmap)
                        dict_error.update({counter:error})
                        dict_coords.update({counter:[(start[1],start[0]), (end[1],end[0])]})
                                    
                        if error < best_score:
          
                            print("current best error", error)
                            best_canvas = img_canvas.copy()
                            best_score = error
                            start_coords = (start[1],start[0])
                            end_coords = (end[1],end[0])
    
                        counter = counter + 1
                        

      
        # sfmap_copy = cancel_out(sfmap_copy,best_canvas)
        qualified_coords_pair = [start_coords,end_coords]            
                
    return qualified_coords_pair,best_canvas,best_score, dict_error,dict_coords

def draw_road_singleline_fast(sfmap, dict_error,dict_coords):
    '''
    fast: cong dierlun kaishi,buzai bianli renyiliangge pixel. ershijiyu diyilun bianli de diandui de jieguo
    For each 128x128 historical map, the roads are drawn based on the filtered the coordinates.
    only one symbol is ued 

    Parameters
    ----------
    sfmap : TYPE
        DESCRIPTION.
    coordinates : TYPE
        DESCRIPTION.

    Returns
    -------
    qualified_coords_pairs : TYPE
        DESCRIPTION.

    '''
    
    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255
    sfmap_copy = sfmap.copy()
    best_score = 999
    best_canvas = None
    start_coords = None # will be used to store the quantified paires
    end_coords = None # will be used to store the quantified paires
    qualified_coords_pair = None

    
    if (len(dict_error)>1):
        list_error = list(dict_error.values())
        # threshold1 = np.percentile(np.array(list_error), 100)
        # threshold2 = np.percentile(np.array(list_error), 85)
        
        dict_error_copy = {k: v for k, v in dict_error.items()}
        for key in dict_error_copy:
            coordinates = dict_coords[key] 
            img_canvas[:,:,:] = 255


            dl.draw_single_line(img_canvas, coordinates[0], coordinates[1], thickness=2)


            error = dl.evaluate(img_canvas, sfmap)
                        
            if error < best_score:
  
                print("current best error", error)
                best_canvas = img_canvas.copy()
                best_score = error
                start_coords = coordinates[0]
                end_coords = coordinates[1]
      
        # sfmap_copy = cancel_out(sfmap_copy,best_canvas)
        qualified_coords_pair = [start_coords,end_coords]

            
                
    return qualified_coords_pair,best_canvas,best_score

def draw_road_dashed_line(sfmap, clusters):
    '''
    For each 128x128 historical map, the roads are drawn based on the filtered the coordinates.
    only one symbol is ued 

    Parameters
    ----------
    sfmap : TYPE
        DESCRIPTION.
    coordinates : TYPE
        DESCRIPTION.

    Returns
    -------
    qualified_coords_pairs : TYPE
        DESCRIPTION.

    '''
    
    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255
    sfmap_copy = sfmap.copy()

    best_score = 999
    best_canvas = None
    start_coords = None # will be used to store the quantified paires
    end_coords = None # will be used to store the quantified paires
    qualified_coords_pair = None    
    dict_error = {}
    dict_coords = {}
    
    if (len(clusters)>=1):
    
        run_times = 0
        counter = 0  

        print("run times", run_times)
        
        for k in range(len(clusters)):
            coordinates = clusters[k]

            for i in range(len(coordinates)-1):
                start = coordinates[i]
                for j in range(0, len(coordinates)):
                    if i!=j:
                        img_canvas[:,:,:] = 255
                        end = coordinates[j]
    
    
                        dl.draw_dashed_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2, length=10, gap=8)
        
                        error = dl.evaluate(img_canvas, sfmap)
                                    
                        dict_error.update({counter:error})
                        dict_coords.update({counter:[(start[1],start[0]), (end[1],end[0])]})
                                    
                        if error < best_score:
          
                            print("current best error", error)
                            best_canvas = img_canvas.copy()
                            best_score = error
                            start_coords = (start[1],start[0])
                            end_coords = (end[1],end[0])
                            
                        counter = counter + 1
                            

      
        # sfmap_copy = cancel_out(sfmap_copy,best_canvas)
        qualified_coords_pair = [start_coords,end_coords]
        run_times = run_times + 1
            
                
    return qualified_coords_pair,best_canvas,best_score,dict_error,dict_coords

def draw_road_dashed_line_fast(sfmap, dict_error, dict_coords):
    '''
    For each 128x128 historical map, the roads are drawn based on the filtered the coordinates.
    only one symbol is ued 

    Parameters
    ----------
    sfmap : TYPE
        DESCRIPTION.
    coordinates : TYPE
        DESCRIPTION.

    Returns
    -------
    qualified_coords_pairs : TYPE
        DESCRIPTION.

    '''
    
    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255
    sfmap_copy = sfmap.copy()
    best_score = 999
    best_canvas = None
    start_coords = None # will be used to store the quantified paires
    end_coords = None # will be used to store the quantified paires
    qualified_coords_pair = None

    
    if (len(dict_error)>1):
    
        list_error = list(dict_error.values())
        
        # threshold1 = np.percentile(np.array(list_error), 15)
        # threshold2 = np.percentile(np.array(list_error), 85)
        
        dict_error_copy = {k: v for k, v in dict_error.items() }
        for key in dict_error_copy:
            coordinates = dict_coords[key] 
            img_canvas[:,:,:] = 255


            dl.draw_dashed_line(img_canvas, coordinates[0], coordinates[1], thickness=2, length=10, gap=8)


            error = dl.evaluate(img_canvas, sfmap)
                        
            if error < best_score:
  
                print("current best error", error)
                best_canvas = img_canvas.copy()
                best_score = error
                start_coords = coordinates[0]
                end_coords = coordinates[1]
      
        # sfmap_copy = cancel_out(sfmap_copy,best_canvas)
        qualified_coords_pair = [start_coords,end_coords]

            
                
    return qualified_coords_pair,best_canvas,best_score


def draw_road_double_lines(sfmap, clusters):
    '''
    For each 128x128 historical map, the roads are drawn based on the filtered the coordinates.
    only one symbol is ued 

    Parameters
    ----------
    sfmap : TYPE
        DESCRIPTION.
    coordinates : TYPE
        DESCRIPTION.

    Returns
    -------
    qualified_coords_pairs : TYPE
        DESCRIPTION.

    '''
    
    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255
    sfmap_copy = sfmap.copy()

    best_score = 999
    best_canvas = None
    start_coords = None # will be used to store the quantified paires
    end_coords = None # will be used to store the quantified paires
    qualified_coords_pair = None
    dict_error = {}
    dict_coords = {}
    
    
    if (len(clusters)>=1):
    
        run_times = 0
        counter = 0  

        print("run times", run_times)
        
        for k in range(len(clusters)):
            coordinates = clusters[k]

            for i in range(len(coordinates)-1):
                start = coordinates[i]
                for j in range(0, len(coordinates)):
                    if i!=j:
                        img_canvas[:,:,:] = 255
                        end = coordinates[j]
                        
                        dl.draw_thick_thin_line(img_canvas, (start[1],start[0]), (end[1],end[0]), spacing=8, left_thickness=2, right_thickness=2)
        
                        error = dl.evaluate(img_canvas, sfmap)
                                                   
                        dict_error.update({counter:error})
                        dict_coords.update({counter:[(start[1],start[0]), (end[1],end[0])]})
                                    
                        if error < best_score:
          
                            print("current best error", error)
                            best_canvas = img_canvas.copy()
                            best_score = error
                            start_coords = (start[1],start[0])
                            end_coords = (end[1],end[0])
                        
                        counter = counter + 1
                        
        # sfmap_copy = cancel_out(sfmap_copy,best_canvas)
        qualified_coords_pair = [start_coords,end_coords]
        run_times = run_times + 1
            
                
    return qualified_coords_pair,best_canvas,best_score,dict_error,dict_coords

def draw_road_double_lines_fast(sfmap, dict_error, dict_coords):
    '''
    For each 128x128 historical map, the roads are drawn based on the filtered the coordinates.
    only one symbol is ued 

    Parameters
    ----------
    sfmap : TYPE
        DESCRIPTION.
    coordinates : TYPE
        DESCRIPTION.

    Returns
    -------
    qualified_coords_pairs : TYPE
        DESCRIPTION.

    '''
    
    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255
    sfmap_copy = sfmap.copy()
    best_score = 999
    best_canvas = None
    start_coords = None # will be used to store the quantified paires
    end_coords = None # will be used to store the quantified paires
    qualified_coords_pair = None

    
    if (len(dict_error)>1):
    
        list_error = list(dict_error.values())
        
        # threshold1 = np.percentile(np.array(list_error), 15)
        # threshold2 = np.percentile(np.array(list_error), 85)
        
        dict_error_copy = {k: v for k, v in dict_error.items() }
        for key in dict_error_copy:
            coordinates = dict_coords[key] 
            img_canvas[:,:,:] = 255


            dl.draw_thick_thin_line(img_canvas, coordinates[0], coordinates[1], spacing=8, left_thickness=2, right_thickness=2)


            error = dl.evaluate(img_canvas, sfmap)
                        
            if error < best_score:
  
                print("current best error", error)
                best_canvas = img_canvas.copy()
                best_score = error
                start_coords = coordinates[0]
                end_coords = coordinates[1]
      
        # sfmap_copy = cancel_out(sfmap_copy,best_canvas)
        qualified_coords_pair = [start_coords,end_coords]

            
                
    return qualified_coords_pair,best_canvas,best_score


def draw_road_solid_dashed_line(sfmap, clusters):
    '''
    For each 128x128 historical map, the roads are drawn based on the filtered the coordinates.
    only one symbol is ued 

    Parameters
    ----------
    sfmap : TYPE
        DESCRIPTION.
    coordinates : TYPE
        DESCRIPTION.

    Returns
    -------
    qualified_coords_pairs : TYPE
        DESCRIPTION.

    '''
    
    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255
    sfmap_copy = sfmap.copy()

    best_score = 999
    best_canvas = None
    start_coords = None # will be used to store the quantified paires
    end_coords = None # will be used to store the quantified paires
    qualified_coords_pair = None
    dict_error = {}
    dict_coords = {}
    
    
    if (len(clusters)>=1):
    
        run_times = 0
        counter = 0  

        print("run times", run_times)
        
        for k in range(len(clusters)):
            coordinates = clusters[k]

            for i in range(len(coordinates)-1):
                start = coordinates[i]
                for j in range(0, len(coordinates)):
                    if i!=j:
                        img_canvas[:,:,:] = 255
                        end = coordinates[j]
    
                        dl.draw_single_dashed_line(img_canvas, (start[1],start[0]), (end[1],end[0]), spacing=5, left_thickness=2, right_thickness=2, length=8, gap=6)
        
                        error = dl.evaluate(img_canvas, sfmap)
            
                        dict_error.update({counter:error})
                        dict_coords.update({counter:[(start[1],start[0]), (end[1],end[0])]})
                                    
                        if error < best_score:
          
                            print("current best error", error)
                            best_canvas = img_canvas.copy()
                            best_score = error
                            start_coords = (start[1],start[0])
                            end_coords = (end[1],end[0])
                        
                        counter = counter + 1
      
        # sfmap_copy = cancel_out(sfmap_copy,best_canvas)
        qualified_coords_pair = [start_coords,end_coords]
        run_times = run_times + 1
            
                
    return qualified_coords_pair,best_canvas,best_score,dict_error,dict_coords

def draw_road_solid_dashed_line_fast(sfmap, dict_error, dict_coords):
    '''
    For each 128x128 historical map, the roads are drawn based on the filtered the coordinates.
    only one symbol is ued 

    Parameters
    ----------
    sfmap : TYPE
        DESCRIPTION.
    coordinates : TYPE
        DESCRIPTION.

    Returns
    -------
    qualified_coords_pairs : TYPE
        DESCRIPTION.

    '''
    
    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255
    sfmap_copy = sfmap.copy()
    best_score = 999
    best_canvas = None
    start_coords = None # will be used to store the quantified paires
    end_coords = None # will be used to store the quantified paires
    qualified_coords_pair = None

    
    if (len(dict_error)>1):
    
        list_error = list(dict_error.values())
        
        # threshold1 = np.percentile(np.array(list_error), 15)
        # threshold2 = np.percentile(np.array(list_error), 85)
        
        dict_error_copy = {k: v for k, v in dict_error.items()}
        for key in dict_error_copy:
            coordinates = dict_coords[key] 
            img_canvas[:,:,:] = 255


            dl.draw_single_dashed_line(img_canvas, coordinates[0], coordinates[1], spacing=5, left_thickness=2, right_thickness=2, length=8, gap=6)


            error = dl.evaluate(img_canvas, sfmap)
                        
            if error < best_score:
  
                print("current best error", error)
                best_canvas = img_canvas.copy()
                best_score = error
                start_coords = coordinates[0]
                end_coords = coordinates[1]
      
        # sfmap_copy = cancel_out(sfmap_copy,best_canvas)
        qualified_coords_pair = [start_coords,end_coords]

            
                
    return qualified_coords_pair,best_canvas,best_score

def draw_road_thick_thin_line(sfmap, clusters):
    '''
    For each 128x128 historical map, the roads are drawn based on the filtered the coordinates.
    only one symbol is ued 

    Parameters
    ----------
    sfmap : TYPE
        DESCRIPTION.
    coordinates : TYPE
        DESCRIPTION.

    Returns
    -------
    qualified_coords_pairs : TYPE
        DESCRIPTION.

    '''
    
    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255
    sfmap_copy = sfmap.copy()

    best_score = 999
    best_canvas = None
    start_coords = None # will be used to store the quantified paires
    end_coords = None # will be used to store the quantified paires
    qualified_coords_pair = None
    dict_error = {}
    dict_coords = {}
    
    if (len(clusters)>=1):
    
        run_times = 0
        counter = 0  

        print("run times", run_times)
        
        for k in range(len(clusters)):
            coordinates = clusters[k]

            for i in range(len(coordinates)-1):
                start = coordinates[i]
                for j in range(0, len(coordinates)):
                    if i!=j:
                        img_canvas[:,:,:] = 255
                        end = coordinates[j]
    
                        dl.draw_thick_thin_line(img_canvas, (start[1],start[0]), (end[1],end[0]), spacing=10, left_thickness=4, right_thickness=2)
        
                        error = dl.evaluate(img_canvas, sfmap)
                                    
                       
                        dict_error.update({counter:error})
                        dict_coords.update({counter:[(start[1],start[0]), (end[1],end[0])]})
                                    
                        if error < best_score:
          
                            print("current best error", error)
                            best_canvas = img_canvas.copy()
                            best_score = error
                            start_coords = (start[1],start[0])
                            end_coords = (end[1],end[0])
                        
                        counter = counter + 1
      
        # sfmap_copy = cancel_out(sfmap_copy,best_canvas)
        qualified_coords_pair = [start_coords,end_coords]
        run_times = run_times + 1
            
                
    return qualified_coords_pair,best_canvas,best_score,dict_error,dict_coords

def draw_road_thick_thin_line_fast(sfmap, dict_error, dict_coords):
    '''
    For each 128x128 historical map, the roads are drawn based on the filtered the coordinates.
    only one symbol is ued 

    Parameters
    ----------
    sfmap : TYPE
        DESCRIPTION.
    coordinates : TYPE
        DESCRIPTION.

    Returns
    -------
    qualified_coords_pairs : TYPE
        DESCRIPTION.

    '''
    
    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255
    sfmap_copy = sfmap.copy()
    best_score = 999
    best_canvas = None
    start_coords = None # will be used to store the quantified paires
    end_coords = None # will be used to store the quantified paires
    qualified_coords_pair = None

    
    if (len(dict_error)>1):
    
        list_error = list(dict_error.values())
        
        # threshold1 = np.percentile(np.array(list_error), 15)
        # threshold2 = np.percentile(np.array(list_error), 85)
        
        dict_error_copy = {k: v for k, v in dict_error.items()}
        for key in dict_error_copy:
            coordinates = dict_coords[key] 
            img_canvas[:,:,:] = 255

 
            dl.draw_thick_thin_line(img_canvas, coordinates[0], coordinates[1], spacing=10, left_thickness=4, right_thickness=2)

            error = dl.evaluate(img_canvas, sfmap)
                        
            if error < best_score:
  
                print("current best error", error)
                best_canvas = img_canvas.copy()
                best_score = error
                start_coords = coordinates[0]
                end_coords = coordinates[1]
      
        # sfmap_copy = cancel_out(sfmap_copy,best_canvas)
        qualified_coords_pair = [start_coords,end_coords]

            
                
    return qualified_coords_pair,best_canvas,best_score

def draw_roads_with_pairs(qualified_coords_pairs, sfmap):
    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255
    for i in range(len(qualified_coords_pairs)):
        start_coords = qualified_coords_pairs[i][0]
        end_coords = qualified_coords_pairs[i][1]
        
        dl.draw_single_line(img_canvas, (start_coords[0],start_coords[1]), (end_coords[0],end_coords[1]), thickness=2)
    cv2.imwrite("output/best_siegfried_canvas0720.png", img_canvas)                

    
def add_roads_up(qualified_coords_pairs, sfmap, list_categories):

    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255

    for i in range(0,len(qualified_coords_pairs)):
        coords = qualified_coords_pairs[i]
        start = coords[0]
        end = coords[1]
        category = list_categories[i]
        if category == 0:
            dl.draw_single_line(img_canvas, (start[0],start[1]), (end[0],end[1]), thickness=2)
        elif category == 1:
            dl.draw_thick_thin_line(img_canvas, (start[0],start[1]), (end[0],end[1]), spacing=8, left_thickness=2, right_thickness=2)
        elif category == 2:
            dl.draw_thick_thin_line(img_canvas, (start[0],start[1]), (end[0],end[1]), spacing=10, left_thickness=4, right_thickness=2)
        elif category == 3:
            dl.draw_dashed_line(img_canvas, (start[0],start[1]), (end[0],end[1]), thickness=2, length=9, gap=8)
        elif category == 4:
            dl.draw_single_dashed_line(img_canvas, (start[0],start[1]), (end[0],end[1]), spacing=8, left_thickness=2, right_thickness=2, length=8, gap=6)

        # if category == 1:
        #     dl.draw_single_line(img_canvas, (start[0],start[1]), (end[0],end[1]), thickness=2)
        # elif category == 3:
        #     dl.draw_thick_thin_line(img_canvas, (start[0],start[1]), (end[0],end[1]), spacing=8, left_thickness=2, right_thickness=2)
        # elif category == 4:
        #     dl.draw_thick_thin_line(img_canvas, (start[0],start[1]), (end[0],end[1]), spacing=10, left_thickness=4, right_thickness=2)
        # elif category == 2:
        #     dl.draw_dashed_line(img_canvas, (start[0],start[1]), (end[0],end[1]), thickness=2, length=9, gap=8)
        # elif category == 0:
        #     dl.draw_single_dashed_line(img_canvas, (start[0],start[1]), (end[0],end[1]), spacing=5, left_thickness=2, right_thickness=2, length=8, gap=6)

    return img_canvas


def classify_road(blacklayer, clusters):
    sfmap_copy = blacklayer.copy()
    qualified_coords_pairs = []
    list_categories = []

    
    if len(clusters)>=1: ## at least one cluster of points are selected as candidates
        
        # to calculate the loss errors in the first loop

        for i in range(len(clusters)):
            list_best_score = []
            list_best_canvas = []
            list_coords_pair = []
            best_score = None
            idx_best_score = None
            best_canvas = None
            #two cases given a pair of points
            qualified_coords_pair = None
            qualified_coords_pair1 = None
            
            cluster = clusters
            if len(cluster)==0:
                continue
            start = cluster[0]
            end = cluster[-1]
            start_coords = (start[1],start[0])
            end_coords = (end[1],end[0])
            qualified_coords_pair = [start_coords, end_coords]
            qualified_coords_pair1 = [end_coords, start_coords]
            
            #switch the start and end
                   

#
            #The first priority : solid line
            img_canvas1 = blacklayer.copy()
            img_canvas1[:,:,:] = 255
            dl.draw_single_line(img_canvas1, (start[1],start[0]), (end[1],end[0]), thickness=2)        
            error1 = dl.evaluate(img_canvas1, sfmap_copy)
            # switch the start and end
            img_canvas11 = blacklayer.copy()
            img_canvas11[:,:,:] = 255
            dl.draw_single_line(img_canvas11, (end[1],end[0]), (start[1],start[0]), thickness=2)        
            error11 = dl.evaluate(img_canvas11, sfmap_copy)
            if error11<error1:
                list_best_score.append(error11)
                list_best_canvas.append(img_canvas11)
                list_coords_pair.append(qualified_coords_pair1)
            else:            
                list_best_score.append(error1)
                list_best_canvas.append(img_canvas1)
                list_coords_pair.append(qualified_coords_pair)
            


            
            #The second priority: 
            img_canvas2 = blacklayer.copy()
            img_canvas2[:,:,:] = 255
            dl.draw_thick_thin_line(img_canvas2, (start[1],start[0]), (end[1],end[0]), spacing=10, left_thickness=2, right_thickness=2)        
            error2 = dl.evaluate(img_canvas2, sfmap_copy)
            
            img_canvas21 = blacklayer.copy()
            img_canvas21[:,:,:] = 255
            dl.draw_thick_thin_line(img_canvas21, (end[1],end[0]), (start[1],start[0]), spacing=10, left_thickness=2, right_thickness=2)        
            error21 = dl.evaluate(img_canvas21, sfmap_copy)
            if error21<error2:
                list_best_score.append(error21)
                list_best_canvas.append(img_canvas21)
                list_coords_pair.append(qualified_coords_pair1)
            else:            
                list_best_score.append(error2)
                list_best_canvas.append(img_canvas2)
                list_coords_pair.append(qualified_coords_pair)

            #The third priority
            img_canvas3 = blacklayer.copy()
            img_canvas3[:,:,:] = 255
            dl.draw_thick_thin_line(img_canvas3, (start[1],start[0]), (end[1],end[0]), spacing=10, left_thickness=4, right_thickness=2)     
            error3 = dl.evaluate(img_canvas3, sfmap_copy)
            
            img_canvas31 = blacklayer.copy()
            img_canvas31[:,:,:] = 255
            dl.draw_thick_thin_line(img_canvas31, (end[1],end[0]), (start[1],start[0]), spacing=10, left_thickness=4, right_thickness=2)     
            error31 = dl.evaluate(img_canvas31, sfmap_copy)
            if error31<error3:
                list_best_score.append(error31)
                list_best_canvas.append(img_canvas31)
                list_coords_pair.append(qualified_coords_pair1)
            else:            
                list_best_score.append(error3)
                list_best_canvas.append(img_canvas3)
                list_coords_pair.append(qualified_coords_pair)


            #The fourth priority
            img_canvas4 = blacklayer.copy()
            img_canvas4[:,:,:] = 255
            dl.draw_dashed_line(img_canvas4, (start[1],start[0]), (end[1],end[0]), thickness=2, length=8, gap=6)        
            error4 = dl.evaluate(img_canvas4, sfmap_copy)
            
            img_canvas41 = blacklayer.copy()
            img_canvas41[:,:,:] = 255
            dl.draw_dashed_line(img_canvas41, (end[1],end[0]), (start[1],start[0]),  thickness=2, length=8, gap=6)        
            error41 = dl.evaluate(img_canvas41, sfmap_copy)
            if error41<error4:
                list_best_score.append(error41)
                list_best_canvas.append(img_canvas41)
                list_coords_pair.append(qualified_coords_pair1)
            else:            
                list_best_score.append(error4)
                list_best_canvas.append(img_canvas4)
                list_coords_pair.append(qualified_coords_pair)



            #The fifth priority
            img_canvas5 = blacklayer.copy()
            img_canvas5[:,:,:] = 255
            dl.draw_single_dashed_line(img_canvas5, (start[1],start[0]), (end[1],end[0]), spacing=6, left_thickness=2, right_thickness=2, length=12, gap=8)        
            error5 = dl.evaluate(img_canvas5, sfmap_copy)
            
            img_canvas51 = blacklayer.copy()
            img_canvas51[:,:,:] = 255
            dl.draw_single_dashed_line(img_canvas51,(end[1],end[0]), (start[1],start[0]), spacing=6, left_thickness=2, right_thickness=2, length=12, gap=8)        
            error51 = dl.evaluate(img_canvas51, sfmap_copy)
            if error51<error5:
                list_best_score.append(error51)
                list_best_canvas.append(img_canvas51)
                list_coords_pair.append(qualified_coords_pair1)
            else:            
                list_best_score.append(error5)
                list_best_canvas.append(img_canvas5)
                list_coords_pair.append(qualified_coords_pair)
            
            

    
            
            #Find the best score
            best_score = min(list_best_score)

            idx_best_score = list_best_score.index(best_score)
            best_canvas = list_best_canvas[idx_best_score]
            list_categories.append(idx_best_score)
            #Cancel out the drawn road
            plt.imshow(sfmap_copy)
            plt.show()
            sfmap_copy = cancel_out(sfmap_copy,list_best_canvas[4])
            # sfmap_copy = cancel_out(sfmap_copy,best_canvas)
            plt.imshow(list_best_canvas[4])
            plt.show()
            plt.imshow(sfmap_copy)
            plt.show()
    
            qualified_coords_pairs.append(list_coords_pair[idx_best_score])
                


    return qualified_coords_pairs,list_categories


    
def priorite_to_class(list_class):
    new_list_class = list_class.copy()
    for i in range(len(list_class)):
        for j in range(len(list_class[i])):
            if list_class[i][j]==0:
                new_list_class[i][j] = 2
            elif list_class[i][j]==1:
                new_list_class[i][j] = 4
            elif list_class[i][j]==2:
                new_list_class[i][j] = 5
            elif list_class[i][j]==3:
                new_list_class[i][j] = 1
            elif list_class[i][j]==4:
                new_list_class[i][j] = 3
                
    return new_list_class
        



                




if __name__ == '__main__':
    
    # ###The first step is to put all the 128x128 maps and skeleton in two lists respectively
    # inpath_map = r"clips_map/"
    # inpath_black_layer = r"clips_black_layer_erosion_remove/"
    # inpath_skeleton = r"clips_skeleton/"
    # list_map = []
    # list_black_layer = []
    

        
    
    # for filename in os.listdir(inpath_skeleton):
    #     infile = inpath_skeleton + filename
    #     print(infile)
    #     # filename_noexe = filename.split('.')[0]      
    #     ds = gdal.Open(infile)
    #     im_bands = ds.RasterCount
    #     band = ds.GetRasterBand(1)
    #     im_width = ds.RasterXSize    
    #     im_height = ds.RasterYSize
    #     im_data = ds.ReadAsArray(0,0,im_width,im_height)
    #     im_data_arr = np.moveaxis(im_data, 0, -1)
    #     list_black_layer.append(im_data_arr)
    #     pickle.dump(list_black_layer,open('list_skeleton.pkl','wb'))

        
    # ###the second step is to draw roads based on maps and filtered coordinates    
    # list_map = pickle.load(open('list_map.pkl','rb'))
    list_black_layer = pickle.load(open('list_black_layer.pkl','rb'))
    list_skeleton = pickle.load(open('list_skeleton.pkl','rb'))
    clusters_list = pickle.load(open('new_clusters_list1208.pkl','rb'))
    # list_coordinates = filter_coordinates(list_skeleton)
    list_qualified_pair = []
    list_class = []
    
    for i in range(265,2090):
        print(i)
        # sfmap = list_map[i]
        blacklayer = list_black_layer[i]
        clusters = clusters_list[i]
        cluster = clusters[0]+clusters[1]
        qualified_coords_pairs,list_categories  = classify_road(blacklayer, cluster)
        # qualified_coords_pairs,list_categories  = classify_road(blacklayer, clusters)
        list_qualified_pair.append(qualified_coords_pairs)
        list_class.append(list_categories)
        final_canvas = add_roads_up(qualified_coords_pairs,blacklayer,list_categories)
        name = '%04d' % (i+1) 
        cv2.imwrite("output/best_siegfried_canvas"+name+".png", final_canvas)   
        
        # draw_roads_with_pairs(qualified_coords_pairs, sfmap)
        # draw_roads_with_pairs(qualified_coords_pairs, blacklayer)
    new_list_class = priorite_to_class(list_class)
    pickle.dump(list_qualified_pair, open('qualified_coords_pairs0218.pkl','wb'))
    pickle.dump(new_list_class, open('road_class0218.pkl','wb'))

        