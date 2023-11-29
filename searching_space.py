# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 20:43:09 2022

In this script, Douglas-Peucker algorithm is used for identifying the turning points 
of one curve

@author: cjiao
"""

import os
import cv2
import numpy as np
import pandas as pd
import draw_lines as dl
from osgeo import gdal
import pickle
import math
import matplotlib.pyplot as plt
import rdp

width = 128
resolution = 1.25
top = 272000
left = 620000
right = 628750
bottom = 266000

# transform the circle center coordinates from image coord system to normal system
def transform_coord(xvalues,yvalues): # to normal system
    x_values = []
    y_values = []
    for i in range(len(xvalues)):
        x = xvalues[i]
        y = width - yvalues[i]
        x_values.append(x)
        y_values.append(y)
    return x_values, y_values

# transform the origin of the coordinate system from bottom-left to top-left
def transform_coord_inverse(cluster): # to image system
    pairs = []
    for i in range(len(cluster)):
        x = cluster[i][0]
        y = width - cluster[i][1]
        pair = (y,x)
        pairs.append(pair)
    return pairs

#transform the point coordinates in each 128x128 image to real spatial coordinates in historical map
# xvalues and yvalues are the x and y values of each point on the image. row and col are the location of the image on the map
def imagecord_to_realcord(xvalues,yvalues,row,col, top, left):

    x_zero = left + 128*col*resolution
    y_zero = top - 128*(row+1)*resolution
    newx = [x*resolution+x_zero for x in xvalues]
    newy = [y*resolution+y_zero for y in yvalues]
    return newx,newy


def filter_coordinates(list_black_layer):
    '''
    zaiyong skeleton deqingkuangxia buxuyaozhege hanshu, zheshiyong black layer zuo searching space shihou xuyaode
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

#to check whether two pixels are neighbors
def neighbors(p,q):
    flag = True
    summation = (p[0]-q[0])**2 + (p[1]-q[1])**2
    dist = math.sqrt(summation)
    if dist > math.sqrt(2):
        flag = False
    else:
        flag = True
    
    return flag

def get_line_clusters(orig_img):
    # one cluster is one component
    components = cv2.connectedComponentsWithStats(orig_img, connectivity=8)
    num_components = components[0]
    # clusters = components[2]
    # num_clusters = clusters[:,4]
    cluster_map = components[1]
    #### to plot cluster map
    # cluster_map[cluster_map == 1] = 50
    # cluster_map[cluster_map == 2] = 100
    # cluster_map[cluster_map == 3] = 200
    # fig = plt.imshow(cluster_map,cmap="Blues")
    # fig.axes.get_xaxis().set_visible(False)
    # fig.axes.get_yaxis().set_visible(False)
    # plt.show()
    
    pixels_highdegree = detect_high_degree_pixels(orig_img) #find high-degree pixels
    new_pixels_hd = spatial_coords(pixels_highdegree, 4, top, left)
####loop the clusters and further divide the clusters based on connectivity and direction
    all_clusters = []
    list_curve = []
    tp_list = [] #the list of turning points
    for i in range(1, num_components):
        cluster = np.where(cluster_map==i)
        cluster_list = [(cluster[0][i], cluster[1][i]) for i in range(0,len(cluster[0]))]
        new_cluster = spatial_coords(cluster_list, 4, top, left)
        srt = sorted(new_cluster,key=lambda x: x[0], reverse=True) #rank the list of tuples
        clusters_old = split_cluster_connectivity(srt)
        clusters_c = merge_clusters(clusters_old)
        list_curve.append(clusters_c)
        
        new_cluster_c = add_hd_pixels_to_curve(clusters_c,new_pixels_hd)
        for j in range(len(new_cluster_c)):
            # turning_points = split_cluster_direction(clusters_c[j],5)
            if len(new_cluster_c[j])>1: # at least two points should be inlcluded in the cluster
                turning_points = rdp.rdp(new_cluster_c[j], epsilon=1.5) # The parameter epsilon needs to be tuned
                
                del turning_points[-1] # remove the last element, i.e. end of curve 
                del turning_points[0] # remove the first element, i.e. start of curve 
                tp_list.append(turning_points)
                start = 0
                if len(turning_points)==0:
                    all_clusters.append(new_cluster_c[j])
                else:
                    for k in range(len(turning_points)):
                        turning_point = tuple(turning_points[k])
                        idx = new_cluster_c[j].index(turning_point)
                        temp_cluster = new_cluster_c[j][start:idx+1]
                        all_clusters.append(temp_cluster)
                        start = idx
                        if k==len(turning_points)-1:
                            temp_cluster = new_cluster_c[j][start:len(new_cluster_c[j])]
                            all_clusters.append(temp_cluster)
    
    
    # return jinsizhixiande quxianduan
    # canvas = plot_curves(list_curve,cluster_map)
    # canvas[canvas == 1] = 50
    # canvas[canvas == 2] = 100
    # canvas[canvas == 3] = 150
    # canvas[canvas == 4] = 200
    # from matplotlib import colors
    # cmap = colors.ListedColormap(['white','red', 'green', 'blue','yellow'])
    # # plt.imshow(canvas,cmap="Oranges")
    # fig = plt.matshow(canvas)
    # plt.gcf().set_facecolor("white")    
    # fig.axes.get_xaxis().set_visible(False)
    # fig.axes.get_yaxis().set_visible(False)
    # plt.show()
    
    # canvas = plot_turning_points(tp_list,cluster_map)
    # fig = plt.matshow(canvas)
    # plt.gcf().set_facecolor("white")    
    # fig.axes.get_xaxis().set_visible(False)
    # fig.axes.get_yaxis().set_visible(False)
    # plt.show()

    return all_clusters

# plot the curves that are generated after splitting the roads                
def plot_curves(list_curve,color_map):
    canvas = color_map.copy()
    canvas[:] = 0
    num = 1
    for i in range(len(list_curve)):
        cluster = list_curve[i]
        for j in range(len(cluster)):
            curve = cluster[j]
            pairs = transform_coord_inverse(curve)
            for k in range(len(pairs)):
                pair = pairs[k]
                x = pair[0]
                y = pair[1]
                canvas[x][y] = num
            num = num + 1
    return canvas
            
def plot_turning_points(tp_list,color_map):  
    canvas = color_map.copy()
    canvas[:] = 0

    for i in range(len(tp_list)):
        cluster = tp_list[i]

        pair = transform_coord_inverse(cluster)
        for j in range(len(pair)):

            xs = pair[j][0]
            ys = pair[j][1]
            
            canvas[xs][ys] = 100

    return canvas
      


#transform the image coordinates to normal coordinates ((0,0) is on the bottom left)
def spatial_coords(cluster_list, num, top, left):
    xvalues = []
    yvalues = []
        
    remainder = num % 55 #corresponds to the column index
    row_number = int(num/55) #correspond to the row index
    
    for i in range(len(cluster_list)):
        x = cluster_list[i][1]
        y = cluster_list[i][0]
        xvalues.append(x)
        yvalues.append(y)

    x_values, y_values = transform_coord(xvalues,yvalues)
    # newx,newy = imagecord_to_realcord(x_values,y_values,row_number,remainder, top, left)

    new_cluster = [(x_values[i],y_values[i]) for i in range(len(x_values))]    

    return new_cluster

# split the cluster based on connectivity. The input is the cluster in the form of list        
def split_cluster_connectivity(cluster_list):
    cluster = cluster_list.copy() #the list of coordinates
    remainder = cluster_list.copy()
    clusters = []

    while len(cluster)>0:
        temp_cluster = [] 
        p = cluster[0] # the first point
        temp_cluster.append(p)
        remainder.remove(p)

        stoplist = [-1,0] # to store the length of temp_cluster. if there is no change, then stop the while function
        while (len(remainder)>0)&(stoplist[-2]!=stoplist[-1]):
            for j in range(len(remainder)-1,-1,-1):
                q = remainder[j]
                flag = neighbors(p, q)
                # p and q are neighbors
                if flag:
                    temp_cluster.append(q)
                    p = q
                    del remainder[j]
                
            stoplist.append(len(temp_cluster))

            
        clusters.append(temp_cluster)
        for k in range(len(cluster)-1,-1,-1):
            if cluster[k] in temp_cluster:
                del cluster[k]
    
    return clusters
                

def merge_clusters(clusters):
    '''
    Due to the specific ranking of road pixels, split_cluster_connectivity function
    cannot split the clusters correctly.
    This function aims to merge the clusters based on adjacency relationship

    Parameters
    ----------
    clusters : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    times = 0
    while times <= 3:
        for i in range(len(clusters)-1):
            cluster1 = clusters[i]
            if len(cluster1)>0:
                for j in  range(i+1, len(clusters)):
                    cluster2 = clusters[j]
                    if len(cluster2)>0:
                        flag, Num = check_adjacency(cluster1, cluster2)
                        if flag:
                            if Num==3:
                                clusters[i].extend(cluster2)
                                clusters[j].clear()
                            elif (Num==2):
                                for k in range(len(cluster2)-1,-1,-1):
                                    clusters[i].insert(0, cluster2[k])
                                clusters[j].clear()
                            elif Num==4:
                                for k in range(len(cluster2)-1,-1,-1):
                                    clusters[i].append(cluster2[k])
                                clusters[j].clear()
                            elif Num==1:
                                for k in range(len(cluster2)):
                                    clusters[i].insert(0, cluster2[k])
                                clusters[j].clear()

        times += 1                         

    new_clusters = [x for x in clusters if x != []]   
    return new_clusters

#to check whether two clusters adjacent or not    
def check_adjacency(cluster1, cluster2):
    flag = False
    Num = 0
    
    start1 = cluster1[0]
    end1 = cluster1[-1]
    start2 = cluster2[0]
    end2 = cluster2[-1]
    
    flag1 = neighbors(start1,start2)
    flag2 = neighbors(start1, end2)
    flag3 = neighbors(end1,start2)
    flag4 = neighbors(end1,end2)
    
    if flag1:
        Num = 1
        flag = True
    elif flag2:
        Num = 2
        flag = True
    elif flag3:
        Num = 3
        flag = True
    elif flag4:
        Num = 4
        flag = True
    return flag, Num   
    

def split_cluster_direction(cluster, thres=1):
    '''
    split one cluster into several subclusters by searching for turning points

    Parameters
    ----------
    cluster : TYPE
        DESCRIPTION.
    thres : TYPE, optional
        DESCRIPTION. The default is 1.

    Returns
    -------
    turning_points : TYPE
        DESCRIPTION.

    '''
    clusters = []
    angle_list = []
    delta_x = [0]*thres
    delta_y = [0]*thres

    for i in range(0,len(cluster),thres):
        angle = 0
        if i+thres>=len(cluster):
            start = cluster[i]
            end = cluster[-1]
   
            if (start[0]==end[0]):
                angle = 90
                angle_list.append(angle)
                delta_x.append(0)
                delta_y.append(start[1]-end[1])
   
            else:
                slope = (start[1]-end[1])/(start[0]-end[0])
                angle = math.atan(slope)*180/math.pi
                angle_list.append(angle)
                delta_x.append(start[0]-end[0])
                delta_y.append(start[1]-end[1])
        else:
            start = cluster[i]
            end = cluster[i+thres]
            
            if (start[0]==end[0]):
                angle = 90
                angle_list.append(angle)
                delta_x.append(0)
                delta_y.append(start[1]-end[1])
   
            else:
                slope = (start[1]-end[1])/(start[0]-end[0])
                angle = math.atan(slope)*180/math.pi
                angle_list.append(angle)
                delta_x.append(start[0]-end[0])
                delta_y.append(start[1]-end[1])
    
    turning_points = search_turning_point(angle_list)
    return turning_points

def search_turning_point(angle_list):
    turning_points = []
    df_angle = pd.DataFrame(angle_list)
    filtered_df = df_angle[(df_angle[0]!=90)&(df_angle[0]!=0)]

    idx = filtered_df.index
    filtered_angles = filtered_df[0].values.tolist()
    if len(filtered_angles)>0:
        flag = filtered_angles[0]
        for i in range(1,len(filtered_angles)):
            ratio = flag/filtered_angles[i]
            if ratio < 0:
                turning_points.append(idx[i])
                flag = filtered_angles[i]
            
    return turning_points

def add_hd_pixels_to_curve(clusters,pixels_highdegree):
    '''
    the current gaps are mainly due to the missing of high-degree pixels
    This functions is to add high-degree pixels to the curves as the starts and emds

    Parameters
    ----------
    clusters : TYPE
        DESCRIPTION.
    pixels_highdegree : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    new_clusters = []
    for i in range(len(clusters)):
        cluster = clusters[i].copy()
        start = cluster[0]
        end = cluster[-1]
        for j in range(len(pixels_highdegree)):
            pixel = pixels_highdegree[j]
            flag1 = neighbors(start, pixel)
            flag2 = neighbors(end, pixel)
            if flag1:
                cluster.insert(0,pixel)
            if flag2:
                cluster.insert(len(cluster),pixel)
        new_clusters.append(cluster)
    return new_clusters
            
            
        
    
            
def detect_high_degree_pixels(roads_arr):
    '''
    detect the pixels with high degrees (degree>=3), and save their coordinates

    Parameters
    ----------
    roads_arr : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    ''' 
    pixels = np.where(roads_arr==1) # filter the pixels corresponding to roads
    pixel_list = [(pixels[0][i], pixels[1][i]) for i in range(0,len(pixels[0]))] #represent the pixels in the list of coordinates
    pixels_highdegree = []
    for i in range(len(pixel_list)):
        p = pixel_list[i]
        Num = 0
        for j in range(len(pixel_list)):            
            q = pixel_list[j]
            if p==q:
                continue
            flag = neighbors(p, q)
            if flag:
                Num = Num + 1
        if Num>=3:
            pixels_highdegree.append(p)
    
    return pixels_highdegree
    
      
        
    
def split_cluster_direction1(cluster, thres):
    clusters = []
    angle_list = []
    start = cluster[0]
    for i in range(0,len(cluster),thres):
        angle = 0
        if i+thres>=len(cluster):  
            end = cluster[-1]
            if start[0]==end[0]:
                angle = 0
                angle_list.append(angle)
            elif start[1]==end[1]:
                angle = 90
                angle_list.append(angle)
            else:
                # slope = (start[1]-pixel[1])/(start[0]-pixel[0])
                slope = (start[0]-end[0])/(start[1]-end[1])
                angle = math.atan(slope)*180/math.pi
                angle_list.append(angle)
        else:
            end = cluster[i+thres]
            if start[0]==end[0]:
                angle = 0
                angle_list.append(angle)
            elif start[1]==end[1]:
                angle = 90
                angle_list.append(angle)
            else:
                # slope = (start[1]-pixel[1])/(start[0]-pixel[0])
                slope = (start[0]-end[0])/(start[1]-end[1])
                angle = math.atan(slope)*180/math.pi
                angle_list.append(angle)
        
    return angle_list            


def split_cluster_direction2(cluster, thres):
    clusters = []
    ratio_list = []
    start = cluster[0]
    dist_real = 0
    for i in range(0,len(cluster),thres):
        ratio = 0
        if i+thres>=len(cluster):  
            end = cluster[-1]
            
            summation = (start[0]-end[0])**2 + (start[1]-end[1])**2
            dist_e = math.sqrt(summation) #the Euclidean distance
            # dist_m = abs(start[0]-end[0]) + abs(start[1]-end[1]) #Manhatten distance
            dist_real = calculate_dist(cluster,i)
            ratio = dist_e/dist_real
            ratio_list.append(ratio)
        else:
            end = cluster[i+thres]

            summation = (start[0]-end[0])**2 + (start[1]-end[1])**2
            dist_e = math.sqrt(summation) #the Euclidean distance
            # dist_m = abs(start[0]-end[0]) + abs(start[1]-end[1]) #Manhatten distance
            dist_real = calculate_dist(cluster,i)
            ratio = dist_e/dist_real
            ratio_list.append(ratio)
        
    return ratio_list        

#calculate the real distance of one curve
def calculate_dist(cluster, num):
    dist = 0
    for i in range(len(cluster)-1):
        if i<=num:
            start = cluster[i]
            end = cluster[i+1]
            summation = (start[0]-end[0])**2 + (start[1]-end[1])**2
            dist_e = math.sqrt(summation) #the Euclidean distance
            dist = dist + dist_e
    
    return dist
        
        


if __name__ == '__main__':
    

#####the first step is to read the skeleton image and split them into clusters. One cluster covers the points of one straight line    
    clusters_list = []
    input_path = "clips_skeleton/"
    Num = 0
    for filename in os.listdir(input_path):
        infile = input_path + filename
        print(infile)
        ds = gdal.Open(infile)
        Num = Num + 1
        print(Num)
        if Num >=0: # in order to debug the code
        # roads_arr   = np.array(ds.GetRasterBand(1).ReadAsArray()).astype(np.uint8)
            roads_array = np.array(ds.GetRasterBand(1).ReadAsArray())
            roads_arr_copy = np.where(roads_array<210,1,0) #set values according to the conditions
            roads_arr = roads_arr_copy.astype(np.uint8)
        
            all_clusters = get_line_clusters(roads_arr)
            clusters_list.append(all_clusters)
        
    # pickle.dump(clusters_list, open('clusters_list1205.pkl','wb'))

# # The second step is to convert the coordinate system
    # clusters_list = pickle.load(open('clusters_list1205.pkl','rb'))
    new_clusters_list = []
    for i in range(0,len(clusters_list)):
        clusters = clusters_list[i]
        if len(clusters)==0:
            new_clusters_list.append(clusters)
        else:
            temp = []
            for j in range(len(clusters)):
                cluster = clusters[j]
                pairs = transform_coord_inverse(cluster)
                temp.append(pairs)
            new_clusters_list.append(temp)

    pickle.dump(new_clusters_list, open('new_clusters_list_1.5.pkl','wb'))
