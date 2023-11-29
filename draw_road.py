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

def filter_coordinates(list_black_layer):
    '''
    Filter the coordinates based on the black layer. The coordinates of black pixels will be kept.

    Parameters
    ----------
    list_black_layer : list
        the list of black layers. each black layer correspond to one 128x128 map.

    Returns
    -------
    coordinates : list
        The list of coordinates.

    '''
    coordinates = []
    for i in range(len(list_black_layer)):
        black_layer = list_black_layer[i]
        blcaklayer_arr = np.moveaxis(black_layer, 2, 0)
        thres_arr = np.where(blcaklayer_arr[0] ==0, 1, 0)
        # thres_arr2 = np.where(blcaklayer_arr < 255, 1, 0)
        # thres_arr3 = np.where(blcaklayer_arr < 255, 1, 0)
        # thres_arr = thres_arr1 + thres_arr2 + thres_arr3
        indices_0 = np.argwhere(thres_arr>0)
        coordinates.append(indices_0)

    return coordinates

def filter_coordinates_1channel(list_black_layer):
    '''
    Filter the coordinates based on the black layer. The coordinates of black pixels will be kept.
    
    The input is tif (1 channel)

    Parameters
    ----------
    list_black_layer : list
        the list of black layers. each black layer correspond to one 128x128 map.

    Returns
    -------
    coordinates : list
        The list of coordinates.

    '''
    coordinates = []
    for i in range(len(list_black_layer)):
        black_layer = list_black_layer[i]
        thres_arr = np.where(black_layer ==0, 1, 0)
        indices_0 = np.argwhere(thres_arr>0)
        coordinates.append(indices_0)

    return coordinates


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


# def draw_one_road(img_canvas,sfmap,best_score, delta_loss):    
    
#     dl.draw_single_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=3)
#     error = dl.evaluate(img_canvas, sfmap)
    

#     if error < best_score:
        
#         print("current best error", error)
#         best_canvas = img_canvas.copy()
#         best_score = error
#         start_coords = (start[1],start[0])
#         end_coords = (end[1],end[0])

#         print(start_coords, end_coords)
#         # canceled_coords.append(pair)
#         cv2.imwrite("output/best_siegfried_canvas_"+str(counter)+"_.png", best_canvas)
#         counter = counter + 1
        
#         delta_loss = abs(error-best_score)
                
#     print(best_score)
#     print(start_coords, end_coords)
#     cv2.imwrite("output/best_siegfried_canvas.png", best_canvas)



    
# def check_the_same_line(start, end, start_coords, end_coords):
#     # dist_start = 0
#     # dist_end = 0
    
#     dist_start = abs(start[0]-start_coords[0]) + abs(start[1]-start_coords[1])
#     dist_end = abs(end[0]-end_coords[0]) + abs(end[1]-end_coords[1])

#     return dist_start, dist_end



def draw_road_per_map(sfmap, coordinates):
    '''
    For each 128x128 historical map, the roads are drawn based on the filtered the coordinates

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
    start_coords = None
    end_coords = None
    qualified_coords_pairs = []
    list_best_canvas = []
    
    if len(coordinates)>1: ## at least two points are selected as candidates
        run_times = 0
        counter = 0  
        while run_times < 1:
            print("run times", run_times)
            if run_times == 0:
                for i in range(len(coordinates)-1):
                    start = coordinates[i]
                    for j in range(i+1, len(coordinates)):
                        img_canvas[:,:,:] = 255
                        end = coordinates[j]
                        pair = [start,end]
             
                        dl.draw_single_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2)
                        # dl.draw_dashed_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2, length=10, gap=8)
    
                        # dl.draw_single_dashed_line(img_canvas, (start[1],start[0]), (end[1],end[0]), spacing=4, left_thickness=2, right_thickness=2, length=12, gap=6)
    
                        error = dl.evaluate(img_canvas, sfmap)
                                    
                        if error < best_score:
                                
                            print("current best error", error)
                            best_canvas = img_canvas.copy()
                            best_score = error
                            start_coords = (start[1],start[0])
                            end_coords = (end[1],end[0])
                    
                            print(start_coords, end_coords)
                            # qualified_coords.append(pair)
                            cv2.imwrite("output/best_siegfried_canvas_"+str(counter)+"_.png", best_canvas)
                            counter = counter + 1
                            
            else:
    
                sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                plt.imshow(sfmap_copy)
                plt.show()
    
                best_score = 999
                for i in range(len(coordinates)-1):
                    start = coordinates[i]
                    for j in range(i+1, len(coordinates)):
                        img_canvas[:,:,:] = 255
                        end = coordinates[j]
                        pair = [start,end]
             
                        dl.draw_single_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2)
                        # dl.draw_dashed_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2, length=10, gap=8)
    
                        # dl.draw_single_dashed_line(img_canvas, (start[1],start[0]), (end[1],end[0]), spacing=4, left_thickness=2, right_thickness=2, length=12, gap=6)
                        error = dl.evaluate(img_canvas, sfmap_copy)
                                    
                        if error < best_score:
                                
                            print("current best error", error)
                            best_canvas = img_canvas.copy()
                            best_score = error
                            start_coords = (start[1],start[0])
                            end_coords = (end[1],end[0])
                    
                            print(start_coords, end_coords)
                            # qualified_coords.append(pair)
                            cv2.imwrite("output/best_siegfried_canvas_"+str(counter)+"_.png", best_canvas)
                            counter = counter + 1
                
    
            qualified_coords_pairs.append([start_coords,end_coords])
            list_best_canvas.append(best_canvas)
            run_times = run_times + 1
    
        while run_times < 6:
            print("run times", run_times)
    
            sfmap_copy = cancel_out(sfmap_copy,best_canvas)
            plt.imshow(sfmap_copy)
            plt.show()
    
            best_score = 999
            for i in range(len(coordinates)-1):
                start = coordinates[i]
                for j in range(i+1, len(coordinates)):
                    img_canvas[:,:,:] = 255
                    end = coordinates[j]
                    pair = [start,end]
         
                    dl.draw_dashed_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2, length=10, gap=8)
                    # dl.draw_single_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2)
    
                    error = dl.evaluate(img_canvas, sfmap_copy)
                                
                    if error < best_score:
                            
                        print("current best error", error)
                        best_canvas = img_canvas.copy()
                        best_score = error
                        start_coords = (start[1],start[0])
                        end_coords = (end[1],end[0])
                
                        print(start_coords, end_coords)
                        # qualified_coords.append(pair)
                        cv2.imwrite("output/best_siegfried_canvas_"+str(counter)+"_.png", best_canvas)
                        counter = counter + 1
                
    
            qualified_coords_pairs.append([start_coords,end_coords])
            list_best_canvas.append(best_canvas)
            run_times = run_times + 1
                
    return qualified_coords_pairs,list_best_canvas
                        
    # print(best_score)
    # print(start_coords, end_coords)
    # cv2.imwrite("output/best_siegfried_canvas.png", best_canvas)                

def draw_road_one_symbol(sfmap, coordinates, threshold):
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
    qualified_coords_pairs = []
    list_best_canvas = []
    
    
    if (len(coordinates)>1)&(len(coordinates)<1300):
    
        termination = [2,1]
        previous_best_score = 999
        run_times = 0
        counter = 0
        start_idx = 0
        end_idx = 0
        start_selected = None #will be used to make the start and end points to be selected for searching
        end_selected = None #will be used to make the start and end points to be selected for searching
        
        while termination[-2]-termination[-1] > threshold:
        # while run_times < 5:
            print("run times", run_times)
            if run_times == 0:
                for i in range(len(coordinates)-1):
                    start = coordinates[i]
                    for j in range(i+1, len(coordinates)):
                        img_canvas[:,:,:] = 255
                        end = coordinates[j]
                        pair = [start,end]
             
                        dl.draw_single_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2)
                        # dl.draw_dashed_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2, length=10, gap=8)    
                        # dl.draw_single_dashed_line(img_canvas, (start[1],start[0]), (end[1],end[0]), spacing=4, left_thickness=2, right_thickness=2, length=12, gap=6)
    
                        error = dl.evaluate(img_canvas, sfmap)
                                    
                        if error < best_score:
      
                            print("current best error", error)
                            best_canvas = img_canvas.copy()
                            best_score = error
                            start_coords = (start[1],start[0])
                            end_coords = (end[1],end[0])
                            start_selected = (start[0],start[1])
                            end_selected = (end[0],end[1])
                            start_idx = i
                            end_idx = j
                    
                            # print(start_coords, end_coords)
                            # qualified_coords.append(pair)
                            # cv2.imwrite("output/best_siegfried_canvas_"+str(counter)+"_.png", best_canvas)
                            counter = counter + 1
              
                sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                termination.append(best_score) 
                qualified_coords_pairs.append([start_coords,end_coords])
                list_best_canvas.append(best_canvas)
                run_times = run_times + 1
                
                #check if it is required to search a line from start/end
                if (start_selected[0]!=0)&(start_selected[0]!=127)&(start_selected[1]!=0)&(start_selected[1]!=127):
                    best_score,best_canvas,start_coords,end_coords = search_line_from_se(start_selected, coordinates, start_idx, img_canvas,sfmap_copy)
                    if termination[-1]-best_score > 0.003:                        
                        sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                        # termination.append(best_score) 
                        qualified_coords_pairs.append([start_coords,end_coords])
                        list_best_canvas.append(best_canvas)
                
                if (end_selected[0]!=0)&(end_selected[0]!=127)&(end_selected[1]!=0)&(end_selected[1]!=127):
                    best_score,best_canvas,start_coords,end_coords = search_line_from_se(end_selected, coordinates, end_idx, img_canvas,sfmap_copy)
                    if termination[-1]-best_score > 0.003:
                        sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                        # termination.append(best_score) 
                        qualified_coords_pairs.append([start_coords,end_coords])
                        list_best_canvas.append(best_canvas)                    
                
            else:
                #### search the optimal line from the top-left coordinate first
                # best_score = 999
                for i in range(len(coordinates)-1):
                    start = coordinates[i]
                    for j in range(i+1, len(coordinates)):
                        img_canvas[:,:,:] = 255
                        end = coordinates[j]
             
                        dl.draw_single_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2)
                        error = dl.evaluate(img_canvas, sfmap_copy)
                                    
                        if error < best_score:                              
                            print("current best error", error)
                            best_canvas = img_canvas.copy()
                            best_score = error
                            start_coords = (start[1],start[0])
                            end_coords = (end[1],end[0])  
                            start_selected = (start[0],start[1])
                            end_selected = (end[0],end[1])
                            start_idx = i
                            end_idx = j
                            counter = counter + 1
                
                sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                termination.append(best_score) 
                qualified_coords_pairs.append([start_coords,end_coords])
                list_best_canvas.append(best_canvas)
                run_times = run_times + 1
                
                #check if it is required to search a line from start/end
                if (start_selected[0]!=0)&(start_selected[0]!=127)&(start_selected[1]!=0)&(start_selected[1]!=127):
                    best_score,best_canvas,start_coords,end_coords = search_line_from_se(start_selected, coordinates, start_idx, img_canvas,sfmap_copy)
                    if termination[-1]-best_score > 0.003:
                        sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                        # termination.append(best_score) 
                        qualified_coords_pairs.append([start_coords,end_coords])
                        list_best_canvas.append(best_canvas)
                
                if (end_selected[0]!=0)&(end_selected[0]!=127)&(end_selected[1]!=0)&(end_selected[1]!=127):
                    best_score,best_canvas,start_coords,end_coords = search_line_from_se(end_selected, coordinates, end_idx, img_canvas,sfmap_copy)
                    if termination[-1]-best_score > 0.003:
                        sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                        # termination.append(best_score) 
                        qualified_coords_pairs.append([start_coords,end_coords])
                        list_best_canvas.append(best_canvas)  
    
                
    return qualified_coords_pairs,list_best_canvas


def draw_road_symbols(sfmap, coordinates, threshold):
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
    qualified_coords_pairs = []
    list_best_canvas = []
    
    
    if (len(coordinates)>1):
    
        termination = [2,1]
        previous_best_score = 999
        run_times = 0
        counter = 0
        start_idx = 0
        end_idx = 0
        start_selected = None #will be used to make the start and end points to be selected for searching
        end_selected = None #will be used to make the start and end points to be selected for searching
        
        while (termination[-2]-termination[-1] > threshold)&(run_times<=5):
        # while run_times < 5:
            print("run times", run_times)
            if run_times == 0:
                for i in range(len(coordinates)-1):
                    start = coordinates[i]
                    for j in range(i+1, len(coordinates)):
                        img_canvas[:,:,:] = 255
                        end = coordinates[j]
                        pair = [start,end]
             
                        dl.draw_single_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2)
                        # dl.draw_dashed_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2, length=10, gap=8)    
                        # dl.draw_single_dashed_line(img_canvas, (start[1],start[0]), (end[1],end[0]), spacing=4, left_thickness=2, right_thickness=2, length=12, gap=6)
    
                        error = dl.evaluate(img_canvas, sfmap)
                                    
                        if error < best_score:
      
                            print("current best error", error)
                            best_canvas = img_canvas.copy()
                            best_score = error
                            start_coords = (start[1],start[0])
                            end_coords = (end[1],end[0])
                            start_selected = (start[0],start[1])
                            end_selected = (end[0],end[1])
                            start_idx = i
                            end_idx = j
                    
                            # print(start_coords, end_coords)
                            # qualified_coords.append(pair)
                            # cv2.imwrite("output/best_siegfried_canvas_"+str(counter)+"_.png", best_canvas)
                            counter = counter + 1
              
                sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                termination.append(best_score) 
                qualified_coords_pairs.append([start_coords,end_coords])
                list_best_canvas.append(best_canvas)
                run_times = run_times + 1
                
                #check if it is required to search a line from start/end
                if (start_selected[0]!=0)&(start_selected[0]!=127)&(start_selected[1]!=0)&(start_selected[1]!=127):
                    best_score,best_canvas,start_coords,end_coords = search_line_from_se(start_selected, coordinates, start_idx, img_canvas,sfmap_copy)
                    if termination[-1]-best_score > 0.003:                        
                        sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                        # termination.append(best_score) 
                        qualified_coords_pairs.append([start_coords,end_coords])
                        list_best_canvas.append(best_canvas)
                
                if (end_selected[0]!=0)&(end_selected[0]!=127)&(end_selected[1]!=0)&(end_selected[1]!=127):
                    best_score,best_canvas,start_coords,end_coords = search_line_from_se(end_selected, coordinates, end_idx, img_canvas,sfmap_copy)
                    if termination[-1]-best_score > 0.003:
                        sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                        # termination.append(best_score) 
                        qualified_coords_pairs.append([start_coords,end_coords])
                        list_best_canvas.append(best_canvas)                    
                
            else:
                #### search the optimal line from the top-left coordinate first
                # best_score = 999
                for i in range(len(coordinates)-1):
                    start = coordinates[i]
                    for j in range(i+1, len(coordinates)):
                        img_canvas[:,:,:] = 255
                        end = coordinates[j]
             
                        dl.draw_single_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2)
                        error = dl.evaluate(img_canvas, sfmap_copy)
                                    
                        if error < best_score:                              
                            print("current best error", error)
                            best_canvas = img_canvas.copy()
                            best_score = error
                            start_coords = (start[1],start[0])
                            end_coords = (end[1],end[0])  
                            start_selected = (start[0],start[1])
                            end_selected = (end[0],end[1])
                            start_idx = i
                            end_idx = j
                            counter = counter + 1
                
                sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                termination.append(best_score) 
                qualified_coords_pairs.append([start_coords,end_coords])
                list_best_canvas.append(best_canvas)
                run_times = run_times + 1
                
                #check if it is required to search a line from start/end
                if (start_selected[0]!=0)&(start_selected[0]!=127)&(start_selected[1]!=0)&(start_selected[1]!=127):
                    best_score,best_canvas,start_coords,end_coords = search_line_from_se(start_selected, coordinates, start_idx, img_canvas,sfmap_copy)
                    if termination[-1]-best_score > 0.003:
                        sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                        # termination.append(best_score) 
                        qualified_coords_pairs.append([start_coords,end_coords])
                        list_best_canvas.append(best_canvas)
                
                if (end_selected[0]!=0)&(end_selected[0]!=127)&(end_selected[1]!=0)&(end_selected[1]!=127):
                    best_score,best_canvas,start_coords,end_coords = search_line_from_se(end_selected, coordinates, end_idx, img_canvas,sfmap_copy)
                    if termination[-1]-best_score > 0.003:
                        sfmap_copy = cancel_out(sfmap_copy,best_canvas)
                        # termination.append(best_score) 
                        qualified_coords_pairs.append([start_coords,end_coords])
                        list_best_canvas.append(best_canvas)  
    
                
    return qualified_coords_pairs,list_best_canvas


def search_line_from_se(start, coordinates, idx,img_canvas,sfmap_copy):

    best_score = 999
    best_canvas = None
    for j in range(len(coordinates)):
        img_canvas[:,:,:] = 255
        end = coordinates[j]
        if j==idx:
            continue
        else:  
            dl.draw_single_line(img_canvas, (start[1],start[0]), (end[1],end[0]), thickness=2)
            error = dl.evaluate(img_canvas, sfmap_copy)
                        
            if error < best_score:
                   
                print("current best error", error)
                best_canvas = img_canvas.copy()
                best_score = error
                start_coords = (start[1],start[0])
                end_coords = (end[1],end[0])
        
    return best_score,best_canvas,start_coords,end_coords


def draw_roads_with_pairs(qualified_coords_pairs, sfmap):
    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255
    for i in range(len(qualified_coords_pairs)):
        start_coords = qualified_coords_pairs[i][0]
        end_coords = qualified_coords_pairs[i][1]
        
        dl.draw_single_line(img_canvas, (start_coords[0],start_coords[1]), (end_coords[0],end_coords[1]), thickness=2)
    cv2.imwrite("output/best_siegfried_canvas0720.png", img_canvas)                

    
def add_roads_up(qualified_coords_pairs, sfmap):

    img_canvas = sfmap.copy()
    img_canvas[:,:,:] = 255

    for i in range(0,len(qualified_coords_pairs)):
        coords = qualified_coords_pairs[i]
        start = coords[0]
        end = coords[1]
        # if i>=1:
        #     dl.draw_dashed_line(img_canvas, (start[0],start[1]), (end[0],end[1]), thickness=2, length=10, gap=8)
        # else:
        #     dl.draw_single_line(img_canvas, (start[0],start[1]), (end[0],end[1]), thickness=2)
        
        dl.draw_single_line(img_canvas, (start[0],start[1]), (end[0],end[1]), thickness=2)

    
    return img_canvas


        

        



                




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
    list_map = pickle.load(open('list_map.pkl','rb'))
    list_black_layer = pickle.load(open('list_black_layer.pkl','rb'))
    list_skeleton = pickle.load(open('list_skeleton.pkl','rb'))
    list_coordinates = filter_coordinates(list_skeleton)
    list_qualified_pair = []
    
    for i in range(0,2090):
        # sfmap = list_map[i]
        blacklayer = list_black_layer[i]
        coordinates = list_coordinates[i]
        # qualified_coords_pairs = draw_road_per_map(sfmap, coordinates)
        qualified_coords_pairs, list_best_canvas = draw_road_one_symbol(blacklayer, coordinates, 0.008)
        list_qualified_pair.append(qualified_coords_pairs)
        final_canvas = add_roads_up(qualified_coords_pairs,blacklayer)
        name = '%04d' % (i+1) 
        cv2.imwrite("output/best_siegfried_canvas"+name+".png", final_canvas)   
        
        # draw_roads_with_pairs(qualified_coords_pairs, sfmap)
        # draw_roads_with_pairs(qualified_coords_pairs, blacklayer)
    pickle.dump(list_qualified_pair, open('qualified_coords_pairs0806.pkl','wb'))

        